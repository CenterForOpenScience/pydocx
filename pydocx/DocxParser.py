import logging
import os
import xml.etree.ElementTree as ElementTree
import zipfile

from abc import abstractmethod, ABCMeta
from contextlib import contextmanager
from xml.etree.ElementTree import _ElementInterface

from pydocx.utils import NamespacedNumId
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("NewParser")


# http://openxmldeveloper.org/discussions/formats/f/15/p/396/933.aspx
EMUS_PER_PIXEL = 9525
USE_ALIGNMENTS = True
TAGS_CONTAINING_CONTENT = (
    't',
    'pict',
    'drawing',
    'delText',
    'ins',
)
TAGS_HOLDING_CONTENT_TAGS = (
    'p',
    'tbl',
    'sdt',
)


def remove_namespaces(document):  # remove namespaces

    root = ElementTree.fromstring(document)
    for child in el_iter(root):
        child.tag = child.tag.split("}")[1]
        child.attrib = dict(
            (k.split("}")[-1], v)
            for k, v in child.attrib.items()
        )
    return ElementTree.tostring(root)

# Add some helper functions to Element to make it slightly more readable


def has_child(self, tag):
    """
    Determine if current element has a child. Stop at first child.
    """
    return True if self.find(tag) is not None else False


def has_descendant_with_tag(self, tag):
    """
    Determine if there is a child ahead in the element tree.
    """
    # Get child. stop at first child.
    return True if self.find('.//' + tag) is not None else False


def find_first(self, tag):
    """
    Find the first occurrence of a tag beneath the current element.
    """
    return self.find('.//' + tag)


def find_all(self, tag):
    """
    Find all occurrences of a tag
    """
    return self.findall('.//' + tag)


def el_iter(el):
    """
    Go through all elements
    """
    try:
        return el.iter()
    except AttributeError:
        return el.findall('.//*')


def find_ancestor_with_tag(self, tag):
    """
    Find the first ancestor with that is a `tag`.
    """
    el = self
    while el.parent is not None:
        el = el.parent
        if el.tag == tag:
            return el
    return None


#make all of these attributes of _ElementInterface
setattr(_ElementInterface, 'has_child', has_child)
setattr(_ElementInterface, 'has_descendant_with_tag', has_descendant_with_tag)
setattr(_ElementInterface, 'find_first', find_first)
setattr(_ElementInterface, 'find_all', find_all)
setattr(_ElementInterface, 'find_ancestor_with_tag', find_ancestor_with_tag)
setattr(_ElementInterface, 'parent', None)
setattr(_ElementInterface, 'is_first_list_item', False)
setattr(_ElementInterface, 'is_last_list_item_in_root', False)
setattr(_ElementInterface, 'is_list_item', False)
setattr(_ElementInterface, 'ilvl', None)
setattr(_ElementInterface, 'num_id', None)
setattr(_ElementInterface, 'heading_level', None)
setattr(_ElementInterface, 'is_in_table', False)
setattr(_ElementInterface, 'previous', None)
setattr(_ElementInterface, 'next', None)
setattr(_ElementInterface, 'vmerge_continue', None)
setattr(_ElementInterface, 'row_index', None)
setattr(_ElementInterface, 'column_index', None)
setattr(_ElementInterface, 'is_last_text', False)

# End helpers


@contextmanager
def ZipFile(path):  # This is not needed in python 3.2+
    f = zipfile.ZipFile(path)
    yield f
    f.close()


class DocxParser:
    __metaclass__ = ABCMeta

    def _build_data(self, path, *args, **kwargs):
        with ZipFile(path) as f:
            self.zip_path, _ = os.path.split(f.filename)
            self.document_text = f.read('word/document.xml')
            self.styles_text = f.read('word/styles.xml')
            try:
                self.fonts = f.read('/word/fontTable.xml')
            except KeyError:
                self.fonts = None
            try:  # Only present if there are lists
                self.numbering_text = f.read('word/numbering.xml')
            except KeyError:
                self.numbering_text = None
            try:  # Only present if there are comments
                self.comment_text = f.read('word/comments.xml')
            except KeyError:
                self.comment_text = None
            self.relationship_text = f.read('word/_rels/document.xml.rels')
            zipped_image_files = [
                e for e in f.infolist()
                if e.filename.startswith('word/media/')
            ]
            for e in zipped_image_files:
                f.extract(
                    e.filename,
                    self.zip_path,
                )

        self.root = ElementTree.fromstring(
            remove_namespaces(self.document_text),  # remove the namespaces
        )
        self.numbering_root = None
        if self.numbering_text:
            self.numbering_root = ElementTree.fromstring(
                remove_namespaces(self.numbering_text),
            )
        self.comment_root = None
        if self.comment_text:
            self.comment_root = ElementTree.fromstring(
                remove_namespaces(self.comment_text),
            )

    def _parse_styles(self):
        tree = ElementTree.fromstring(
            remove_namespaces(self.styles_text),
        )
        result = {}
        for style in tree.find_all('style'):
            style_val = style.find_first('name').attrib['val']
            result[style.attrib['styleId']] = style_val
        return result

    def _parse_rels_root(self):
        tree = ElementTree.fromstring(self.relationship_text)
        rels_dict = {}
        for el in tree:
            rId = el.get('Id')
            target = el.get('Target')
            rels_dict[rId] = target
        return rels_dict

    def __init__(self, *args, **kwargs):
        self._parsed = ''
        self.block_text = ''
        self.page_width = 0
        self._build_data(*args, **kwargs)

        def add_parent(el):  # if a parent, make that an attribute
            for child in el.getchildren():
                setattr(child, 'parent', el)
                add_parent(child)

        #divide by 20 to get to pt (Office works in 20th's of a point)
        """
        see http://msdn.microsoft.com/en-us/library/documentformat
        .openxml.wordprocessing.indentation.aspx
        """
        if self.root.find_first('pgSz') is not None:
            self.page_width = int(self.root.
                                  find_first('pgSz').attrib['w']) / 20

        add_parent(self.root)  # create the parent attributes

        #all blank when we init
        self.comment_store = None
        self.visited = []
        self.list_depth = 0
        self.rels_dict = self._parse_rels_root()
        self.styles_dict = self._parse_styles()
        self.parse_begin(self.root)  # begin to parse

    def _filter_children(self, element, tags):
        return [
            el for el in element.getchildren()
            if el.tag in tags
        ]

    def _set_list_attributes(self, el):
        list_elements = el.find_all('numId')
        for li in list_elements:
            parent = li.find_ancestor_with_tag('p')
            # Deleted text in a list will have a numId but no ilvl.
            if parent.find_first('ilvl') is None:
                continue
            parent.is_list_item = True
            parent.num_id = self._generate_num_id(parent)
            parent.ilvl = parent.find_first('ilvl').attrib['val']

    def _generate_num_id(self, el):
        '''
        Fun fact: It is possible to have a list in the root, that holds a table
        that holds a list and for both lists to have the same numId. When this
        happens we should namespace the nested list with the number of tables
        it is in to ensure it is considered a new list. Otherwise all sorts of
        terrible html gets generated.
        '''
        num_id = el.find_first('numId').attrib['val']

        # First, go up the parent until we get None and count the number of
        # tables there are.
        num_tables = 0
        while el.parent is not None:
            if el.tag == 'tbl':
                num_tables += 1
            el = el.parent
        return NamespacedNumId(
            num_id=num_id,
            num_tables=num_tables,
        )

    def _set_table_attributes(self, el):
        tables = el.find_all('tbl')
        for table in tables:
            rows = self._filter_children(table, ['tr'])
            if rows is None:
                continue
            for i, row in enumerate(rows):
                tcs = self._filter_children(row, ['tc'])
                for j, child in enumerate(tcs):
                    child.row_index = i
                    child.column_index = j
                    v_merge = child.find_first('vMerge')
                    if (
                            v_merge is not None and
                            'continue' == v_merge.get('val', '')
                    ):
                        child.vmerge_continue = True

    def _set_text_attributes(self, el):
        # find the ppr. look thru all the elements within and find the text
        #if it's the last item in the list, it's the last text
        paragraph_tag_property = el.find_all('pPr')
        for el in paragraph_tag_property:
            for i, t in enumerate(el.parent.find_all('t')):
                if i == (len(el.parent.find_all('t')) - 1):
                    t.is_last_text = True

    def _set_is_in_table(self, el):
        paragraph_elements = el.find_all('p')
        for p in paragraph_elements:
            if p.find_ancestor_with_tag('tc') is not None:
                p.is_in_table = True

    def _set_first_list_item(self, num_ids, ilvls, list_elements):
        # Lists are grouped by having the same `num_id` and `ilvl`. The first
        # list item is the first list item found for each `num_id` and `ilvl`
        # combination.
        for num_id in num_ids:
            for ilvl in ilvls:
                filtered_list_elements = [
                    i for i in list_elements
                    if (
                        i.num_id == num_id and
                        i.ilvl == ilvl
                    )
                ]
                if not filtered_list_elements:
                    continue
                first_el = filtered_list_elements[0]
                first_el.is_first_list_item = True

    def _set_last_list_item(self, num_ids, list_elements):
        # Find last list elements. Only mark list tags as the last list tag if
        # it is in the root of the document. This is only used to ensure that
        # once a root level list is finished we do not roll in the rest of the
        # non list elements into the first root level list.
        for num_id in num_ids:
            filtered_list_elements = [
                i for i in list_elements
                if i.num_id == num_id
            ]
            if not filtered_list_elements:
                continue
            last_el = filtered_list_elements[-1]
            last_el.is_last_list_item_in_root = True

    def _set_headers(self, elements):
        # These are the styles for headers and what the html tag should be if
        # we have one.
        headers = {
            'heading 1': 'h1',
            'heading 2': 'h2',
            'heading 3': 'h3',
            'heading 4': 'h4',
            'heading 5': 'h5',
            'heading 6': 'h6',
            'heading 7': 'h6',
            'heading 8': 'h6',
            'heading 9': 'h6',
            'heading 10': 'h6',
        }
        for element in elements:
            # This element is using the default style which is not a heading.
            if element.find_first('pStyle') is None:
                continue
            style = element.find_first('pStyle').attrib.get('val', '')
            style = self.styles_dict.get(style)

            # Check to see if this element is actually a header.
            if style and style.lower() in headers:
                # Set all the list item variables to false.
                element.is_list_item = False
                element.is_first_list_item = False
                element.is_last_list_item = False
                # Prime the heading_level
                element.heading_level = headers[style.lower()]

    def _set_next(self, body):
        def _get_children_with_content(el):
            # We only care about children if they have text in them.
            children = []
            for child in self._filter_children(el, TAGS_HOLDING_CONTENT_TAGS):
                has_descendant_with_tag = any(
                    child.has_descendant_with_tag(tag) for
                    tag in TAGS_CONTAINING_CONTENT
                )
                if has_descendant_with_tag:
                    children.append(child)
            return children

        def _assign_next(children):
            # Populate the `next` attribute for all the child elements.
            for i in range(len(children)):
                try:
                    if children[i + 1] is not None:
                        children[i].next = children[i + 1]
                except IndexError:
                    pass
                try:
                    if children[i - 1] is not None:
                        children[i].previous = children[i - 1]
                except IndexError:
                    pass
        # Assign next for everything in the root.
        _assign_next(_get_children_with_content(body))

        # In addition set next for everything in table cells.
        for tc in body.find_all('tc'):
            _assign_next(_get_children_with_content(tc))

    def parse_begin(self, el):
        self._set_list_attributes(el)
        self._set_table_attributes(el)
        self._set_text_attributes(el)
        self._set_is_in_table(el)

        # Find the first and last li elements
        body = el.find_first('body')
        list_elements = [
            child for child in body.find_all('p')
            if child.is_list_item
        ]
        num_ids = set([i.num_id for i in list_elements])
        ilvls = set([i.ilvl for i in list_elements])

        self._set_first_list_item(num_ids, ilvls, list_elements)
        self._set_last_list_item(num_ids, list_elements)
        p_elements = [
            child for child in body.find_all('p')
        ]
        self._set_headers(p_elements)
        self._set_next(body)

        self._parsed += self.parse(el)

    def parse(self, el):
        if el in self.visited:
            return ''
        self.visited.append(el)
        parsed = ''
        for child in el:
            # recursive. So you can get all the way to the bottom
            parsed += self.parse(child)

        if el.tag == 'br' and el.attrib.get('type') == 'page':
            return self.parse_page_break(el, parsed)
        elif el.tag == 'tbl':
            return self.parse_table(el, parsed)
        elif el.tag == 'tr':
            return self.parse_table_row(el, parsed)
        elif el.tag == 'tc':
            return self.parse_table_cell(el, parsed)
        elif el.tag == 'r':
            return self.parse_r(el, parsed)
        elif el.tag == 't':
            return self.parse_t(el, parsed)
        elif el.tag == 'br':
            return self.parse_break_tag(el, parsed)
        elif el.tag == 'delText':
            return self.parse_deletion(el, parsed)
        elif el.tag == 'p':
            return self.parse_p(el, parsed)
        elif el.tag == 'ins':
            return self.parse_insertion(el, parsed)
        elif el.tag == 'hyperlink':
            return self.parse_hyperlink(el, parsed)
        elif el.tag in ('pict', 'drawing'):
            return self.parse_image(el)
        else:
            return parsed

    def parse_page_break(self, el, text):
        #TODO figure out what parsed is getting overwritten
        return self.page_break()

    def parse_table(self, el, text):
        return self.table(text)

    def parse_table_row(self, el, text):
        return self.table_row(text)

    def parse_table_cell(self, el, text):
        v_merge = el.find_first('vMerge')
        if v_merge is not None and 'continue' == v_merge.get('val', ''):
            return ''
        colspan = self.get_colspan(el)
        rowspan = self._get_rowspan(el, v_merge)
        return self.table_cell(text, colspan, rowspan)

    def parse_list(self, el, text):
        """
        All the meat of building the list is done in _parse_list, however we
        call this method for two reasons: It is the naming convention we are
        following. And we need a reliable way to raise and lower the list_depth
        (which is used to determine if we are in a list). I could have done
        this in _parse_list, however it seemed cleaner to do it here.
        """
        self.list_depth += 1
        parsed = self._parse_list(el, text)
        self.list_depth -= 1
        if el.is_in_table:
            return self.parse_table_cell_contents(el, parsed)
        return parsed

    def _build_list(self, el, text):
        # Get the list style for the pending list.
        lst_style = self.get_list_style(
            el.num_id.num_id,
            el.ilvl,
        )

        parsed = text
        # Create the actual list and return it.
        if lst_style == 'bullet':
            return self.unordered_list(parsed)
        else:
            return self.ordered_list(
                parsed,
                lst_style,
            )

    def _parse_list(self, el, text):
        parsed = self.parse_list_item(el, text)
        num_id = el.num_id
        ilvl = el.ilvl
        # Everything after this point assumes the first element is not also the
        # last. If the first element is also the last then early return by
        # building and returning the completed list.
        if el.is_last_list_item_in_root:
            return self._build_list(el, parsed)
        next_el = el.next

        def is_same_list(next_el, num_id, ilvl):
            # Bail if next_el is not an element
            if next_el is None:
                return False
            if next_el.is_last_list_item_in_root:
                return False
            # If next_el is not a list item then roll it into the list by
            # returning True.
            if not next_el.is_list_item:
                return True
            if next_el.num_id != num_id:
                # The next element is a new list entirely
                return False
            if next_el.ilvl < ilvl:
                # The next element is de-indented, so this is really the last
                # element in the list
                return False
            return True

        while is_same_list(next_el, num_id, ilvl):
            if next_el in self.visited:
                # Early continue for elements we have already visited.
                next_el = next_el.next
                continue

            if next_el.is_list_item:
                # Reset the ilvl
                ilvl = next_el.ilvl

            parsed += self.parse(next_el)
            next_el = next_el.next

        def should_parse_last_el(last_el, first_el):
            if last_el is None:
                return False
            # Different list
            if last_el.num_id != first_el.num_id:
                return False
            # Will be handled when the ilvls do match (nesting issue)
            if last_el.ilvl != first_el.ilvl:
                return False
            # We only care about last items that have not been parsed before
            # (first list items are always parsed at the beginning of this
            # method.)
            return (
                not last_el.is_first_list_item and
                last_el.is_last_list_item_in_root
            )
        if should_parse_last_el(next_el, el):
            parsed += self.parse(next_el)

        # If the list has no content, then we don't need to worry about the
        # list styling, because it will be stripped out.
        if parsed == '':
            return parsed

        return self._build_list(el, parsed)

    def parse_p(self, el, text):
        if text == '':
            return ''
        if el.is_first_list_item:
            return self.parse_list(el, text)
        if el.heading_level:
            return self.parse_heading(el, text)
        if el.is_list_item:
            return self.parse_list_item(el, text)
        if el.is_in_table:
            return self.parse_table_cell_contents(el, text)
        parsed = text
        # No p tags in li tags
        if self.list_depth == 0:
            parsed = self.paragraph(parsed)
        return parsed

    def _should_append_break_tag(self, next_el):
        paragraph_like_tags = [
            'p',
        ]
        inline_like_tags = [
            'smartTag',
            'ins',
            'delText',
        ]
        if next_el.is_list_item:
            return False
        if next_el.previous is None:
            return False
        tag_is_inline_like = any(
            next_el.has_descendant_with_tag(tag) for
            tag in inline_like_tags
        )
        if tag_is_inline_like:
            return False
        if next_el.previous.is_last_list_item_in_root:
            return False
        if next_el.previous.tag not in paragraph_like_tags:
            return False
        if next_el.tag not in paragraph_like_tags:
            return False
        return True

    def parse_heading(self, el, parsed):
        return self.heading(parsed, el.heading_level)

    def parse_list_item(self, el, text):
        # If for whatever reason we are not currently in a list, then start
        # a list here. This will only happen if the num_id/ilvl combinations
        # between lists is not well formed.
        parsed = text
        if self.list_depth == 0:
            return self.parse_list(el, parsed)

        def _should_parse_next_as_content(el):
            """
            Get the contents of the next el and append it to the
            contents of the current el (that way things like tables
            are actually in the li tag instead of in the ol/ul tag).
            """
            next_el = el.next
            if next_el is None:
                return False
            if (
                    not next_el.is_list_item and
                    not el.is_last_list_item_in_root
            ):
                return True
            if next_el.is_first_list_item:
                if next_el.num_id == el.num_id:
                    return True
            return False

        while el is not None:
            if _should_parse_next_as_content(el):
                el = el.next
                next_elements_content = self.parse(el)
                if not next_elements_content:
                    continue
                if self._should_append_break_tag(el):
                    parsed += self.break_tag()
                parsed += next_elements_content
            else:
                break
        # Create the actual li element
        return self.list_element(parsed)

    def _get_rowspan(self, el, v_merge):
        current_row = el.row_index
        current_col = el.column_index
        rowspan = 1
        result = ''

        tbl = el.find_ancestor_with_tag('tbl')
        # We only want table cells that have a higher row_index that is greater
        # than the current_row and that are on the current_col
        tcs = [
            tc for tc in tbl.find_all('tc')
            if tc.row_index >= current_row and
            tc.column_index == current_col
        ]
        restart_in_v_merge = False
        if v_merge is not None and 'val' in v_merge.attrib:
            restart_in_v_merge = 'restart' in v_merge.attrib['val']

        def increment_rowspan(tc):
            if not restart_in_v_merge:
                return False
            if not tc.vmerge_continue:
                return False
            return True

        for tc in tcs:
            if increment_rowspan(tc):
                rowspan += 1
            else:
                rowspan = 1
            if rowspan > 1:
                result = rowspan
        return str(result)

    def get_colspan(self, el):
        grid_span = el.find_first('gridSpan')
        if grid_span is None:
            return ''
        return el.find_first('gridSpan').attrib['val']

    def parse_table_cell_contents(self, el, text):
        parsed = text

        def _should_parse_next_as_content(el):
            next_el = el.next
            if next_el is None:
                return False
            if next_el.is_in_table:
                return True
        while el is not None:
            if _should_parse_next_as_content(el):
                el = el.next
                next_elements_content = self.parse(el)
                if not next_elements_content:
                    continue
                if self._should_append_break_tag(el):
                    parsed += self.break_tag()
                parsed += next_elements_content
            else:
                break
        return parsed

    def parse_hyperlink(self, el, text):
        rId = el.get('id')
        href = self.rels_dict.get(rId)
        if not href:
            return text
        href = self.escape(href)
        return self.hyperlink(text, href)

    def _get_image_id(self, el):
        # Drawings
        blip = el.find_first('blip')
        if blip is not None:
            # On drawing tags the id is actually whatever is returned from the
            # embed attribute on the blip tag. Thanks a lot Microsoft.
            return blip.get('embed')
        # Picts
        imagedata = el.find_first('imagedata')
        if imagedata is not None:
            return imagedata.get('id')

    def _convert_image_size(self, size):
        return size / EMUS_PER_PIXEL

    def _get_image_size(self, el):
        """
        If we can't find a height or width, return 0 for whichever is not
        found, then rely on the `image` handler to strip those attributes. This
        functionality can change once we integrate PIL.
        """
        sizes = el.find_first('ext')
        if sizes is not None and sizes.get('cx'):
            if sizes.get('cx'):
                x = self._convert_image_size(int(sizes.get('cx')))
            if sizes.get('cy'):
                y = self._convert_image_size(int(sizes.get('cy')))
            return (
                '%dpx' % x,
                '%dpx' % y,
            )
        shape = el.find_first('shape')
        if shape is not None and shape.get('style') is not None:
            # If either of these are not set, rely on the method `image` to not
            # use either of them.
            x = 0
            y = 0
            styles = shape.get('style').split(';')

            for s in styles:
                if s.startswith('height:'):
                    y = s.split(':')[1]
                if s.startswith('width:'):
                    x = s.split(':')[1]
            return x, y
        return 0, 0

    def parse_image(self, el):
        x, y = self._get_image_size(el)
        rId = self._get_image_id(el)
        src = self.rels_dict.get(rId)
        if not src:
            return ''
        src = os.path.join(
            self.zip_path,
            'word',
            src,
        )
        src = self.escape(src)
        return self.image(src, x, y)

    def _is_style_on(self, el):
        """
        For b, i, u (bold, italics, and underline) merely having the tag is not
        sufficient. You need to check to make sure it is not set to "false" as
        well.
        """
        return el.get('val') != 'false'

    def parse_t(self, el, parsed):
        return self.escape(el.text)

    def parse_break_tag(self, el, parsed):
        return self.break_tag()

    def parse_deletion(self, el, parsed):
        return self.deletion(el.text, '', '')

    def parse_insertion(self, el, parsed):
        return self.insertion(parsed, '', '')

    def parse_r(self, el, parsed):
        """
        Parse the running text.
        """
        block = False
        text = parsed
        if not text:
            return ''
        run_tag_property = el.find('rPr')
        if run_tag_property is not None:
            fns = []
            if run_tag_property.has_child('b'):  # text styling
                if self._is_style_on(run_tag_property.find('b')):
                    fns.append(self.bold)
            if run_tag_property.has_child('i'):
                if self._is_style_on(run_tag_property.find('i')):
                    fns.append(self.italics)
            if run_tag_property.has_child('u'):
                if self._is_style_on(run_tag_property.find('u')):
                    fns.append(self.underline)
            for fn in fns:
                text = fn(text)
        paragraph_tag_property = el.parent.find('pPr')
        just = ''
        if paragraph_tag_property is not None:
            jc = paragraph_tag_property.find('jc')
            if jc is not None:  # text alignments
                if jc.attrib['val'] == 'right':
                    just = 'right'
                elif jc.attrib['val'] == 'center':
                    just = 'center'
                elif jc.attrib['val'] == 'left':
                    just = 'left'
            ind = paragraph_tag_property.find('ind')
            right = ''
            left = ''
            firstLine = ''
            if ind is not None:
                right = None
                left = None
                firstLine = None
                if 'right' in ind.attrib:
                    right = ind.attrib['right']
                    # divide by 20 to get to pt. multiply by (4/3) to get to px
                    right = (int(right) / 20) * float(4) / float(3)
                    right = str(right)
                if 'left' in ind.attrib:
                    left = ind.attrib['left']
                    left = (int(left) / 20) * float(4) / float(3)
                    left = str(left)
                if 'firstLine' in ind.attrib:
                    firstLine = ind.attrib['firstLine']
                    firstLine = (int(firstLine) / 20) * float(4) / float(3)
                    firstLine = str(firstLine)
            if jc is not None or ind is not None:
                t_els = el.find_all('t')
                for el in t_els:
                    if el.is_last_text:
                        block = False
                        self.block_text += text
                        text = self.indent(self.block_text, just,
                                           firstLine, left, right)
                        self.block_text = ''
                    else:
                        block = True
                        self.block_text += text
        if block is False:
            return text
        else:
            return ''

    def get_list_style(self, num_id, ilvl):
        ids = self.numbering_root.find_all('num')
        for _id in ids:
            if _id.attrib['numId'] != num_id:
                continue
            abstractid = _id.find('abstractNumId')
            abstractid = abstractid.attrib['val']
            style_information = self.numbering_root.find_all(
                'abstractNum',
            )
            for info in style_information:
                if info.attrib['abstractNumId'] == abstractid:
                    for i in el_iter(info):
                        if 'ilvl' in i.attrib and i.attrib['ilvl'] != ilvl:
                            continue
                        if i.find('numFmt') is not None:
                            return i.find('numFmt').attrib['val']

    @property
    def parsed(self):
        return self._parsed

    @property
    def escape(self, text):
        return text

    @abstractmethod
    def linebreak(self):
        return ''

    @abstractmethod
    def paragraph(self, text):
        return text

    @abstractmethod
    def heading(self, text, heading_level):
        return text

    @abstractmethod
    def insertion(self, text, author, date):
        return text

    @abstractmethod
    def hyperlink(self, text, href):
        return text

    @abstractmethod
    def image_handler(self, path):
        return path

    @abstractmethod
    def image(self, path, x, y):
        return self.image_handler(path)

    @abstractmethod
    def deletion(self, text, author, date):
        return text

    @abstractmethod
    def bold(self, text):
        return text

    @abstractmethod
    def italics(self, text):
        return text

    @abstractmethod
    def underline(self, text):
        return text

    @abstractmethod
    def tab(self):
        return True

    @abstractmethod
    def ordered_list(self, text):
        return text

    @abstractmethod
    def unordered_list(self, text):
        return text

    @abstractmethod
    def list_element(self, text):
        return text

    @abstractmethod
    def table(self, text):
        return text

    @abstractmethod
    def table_row(self, text):
        return text

    @abstractmethod
    def table_cell(self, text):
        return text

    @abstractmethod
    def page_break(self):
        return True

    @abstractmethod
    def indent(self, text, left='', right='', firstLine=''):
        return text  # TODO JUSTIFIED JUSTIFIED TEXT
