from collections import defaultdict
from lxml import etree


UPPER_ROMAN_TO_HEADING_VALUE = 'h2'
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


def el_iter(el):
    """
    Go through all elements
    """
    try:
        return el.iter()
    except AttributeError:
        return el.findall('.//*')


def remove_namespaces(document):
    # I can't really find a good way to do this with lxml. Se just do it with
    # xml.
    import xml.etree.ElementTree as xml_etree
    root = xml_etree.fromstring(document)
    for child in el_iter(root):
        child.tag = child.tag.split("}")[1]
        child.attrib = dict(
            (k.split("}")[-1], v)
            for k, v in child.attrib.items()
        )
    return xml_etree.tostring(root)


def get_list_style(numbering_root, num_id, ilvl):
    # This is needed on both the custom lxml parser and the pydocx parser. So
    # make it a function.
    ids = numbering_root.find_all('num')
    for _id in ids:
        if _id.attrib['numId'] != num_id:
            continue
        abstractid = _id.find('abstractNumId')
        abstractid = abstractid.attrib['val']
        style_information = numbering_root.find_all(
            'abstractNum',
        )
        for info in style_information:
            if info.attrib['abstractNumId'] == abstractid:
                for i in el_iter(info):
                    if (
                            'ilvl' in i.attrib and
                            i.attrib['ilvl'] != ilvl):
                        continue
                    if i.find('numFmt') is not None:
                        return i.find('numFmt').attrib['val']


class NamespacedNumId(object):
    def __init__(self, num_id, num_tables, *args, **kwargs):
        self._num_id = num_id
        self._num_tables = num_tables

    def __unicode__(self, *args, **kwargs):
        return '%s:%d' % (
            self._num_id,
            self._num_tables,
        )

    def __repr__(self, *args, **kwargs):
        return self.__unicode__(*args, **kwargs)

    def __eq__(self, other):
        if other is None:
            return False
        return repr(self) == repr(other)

    def __ne__(self, other):
        if other is None:
            return False
        return repr(self) != repr(other)

    @property
    def num_id(self):
        return self._num_id


# Since I can't actually set attribute (reliably) on each element. I have to
# keep track of the next and previous elements here.
element_meta_data = defaultdict(dict)


class PydocxLXMLParser(etree.ElementBase):

    @property
    def is_first_list_item(self):
        return element_meta_data[self].get('is_first_list_item', False)

    @property
    def is_last_list_item_in_root(self):
        return element_meta_data[self].get('is_last_list_item_in_root', False)

    @property
    def is_list_item(self):
        return element_meta_data[self].get('is_list_item', False)

    @property
    def num_id(self):
        if not self.is_list_item:
            return None
        return element_meta_data[self].get('num_id')

    @property
    def ilvl(self):
        if not self.is_list_item:
            return None
        return element_meta_data[self].get('ilvl')

    @property
    def heading_level(self):
        return element_meta_data[self].get('heading_level')

    @property
    def is_in_table(self):
        return element_meta_data[self].get('is_in_table')

    @property
    def row_index(self):
        return element_meta_data[self].get('row_index')

    @property
    def column_index(self):
        return element_meta_data[self].get('column_index')

    @property
    def vmerge_continue(self):
        return element_meta_data[self].get('vmerge_continue')

    @property
    def next(self):
        if self not in element_meta_data:
            return
        return element_meta_data[self].get('next')

    @property
    def previous(self):
        if self not in element_meta_data:
            return
        return element_meta_data[self].get('previous')

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

    def find_ancestor_with_tag(self, tag):
        """
        Find the first ancestor with that is a `tag`.
        """
        el = self
        while el.getparent() is not None:
            el = el.getparent()
            if el.tag == tag:
                return el
        return None

    def has_descendant_with_tag(self, tag):
        """
        Determine if there is a child ahead in the element tree.
        """
        # Get child. stop at first child.
        return True if self.find('.//' + tag) is not None else False

    def has_child(self, tag):
        """
        Determine if current element has a child. Stop at first child.
        """
        return True if self.find(tag) is not None else False

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
            if parent is None:
                continue
            if parent.find_first('ilvl') is None:
                continue
            element_meta_data[parent]['is_list_item'] = True
            element_meta_data[parent]['num_id'] = self._generate_num_id(parent)
            element_meta_data[parent]['ilvl'] = parent.find_first(
                'ilvl',
            ).attrib['val']

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
        while el.getparent() is not None:
            if el.tag == 'tbl':
                num_tables += 1
            el = el.getparent()
        return NamespacedNumId(
            num_id=num_id,
            num_tables=num_tables,
        )

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
                element_meta_data[first_el]['is_first_list_item'] = True

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
            element_meta_data[last_el]['is_last_list_item_in_root'] = True

    def _set_table_attributes(self, el):
        tables = el.find_all('tbl')
        for table in tables:
            rows = self._filter_children(table, ['tr'])
            if rows is None:
                continue
            for i, row in enumerate(rows):
                tcs = self._filter_children(row, ['tc'])
                for j, child in enumerate(tcs):
                    element_meta_data[child]['row_index'] = i
                    element_meta_data[child]['column_index'] = j
                    v_merge = child.find_first('vMerge')
                    if (
                            v_merge is not None and
                            'continue' == v_merge.get('val', '')
                    ):
                        element_meta_data[child]['vmerge_continue'] = True

    def _set_is_in_table(self, el):
        paragraph_elements = el.find_all('p')
        for p in paragraph_elements:
            if p.find_ancestor_with_tag('tc') is not None:
                element_meta_data[p]['is_in_table'] = True

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
                element_meta_data[element]['is_list_item'] = False
                element_meta_data[element]['is_first_list_item'] = False
                element_meta_data[element]['is_last_list_item_in_root'] = False
                # Prime the heading_level
                element_meta_data[element]['heading_level'] = headers[style.lower()]  # noqa

    def _convert_upper_roman(self, body):
        if not self.convert_root_level_upper_roman:
            return
        first_root_list_items = [
            # Only root level elements.
            el for el in body.getchildren()
            # And only first_list_items
            if el.is_first_list_item
        ]
        visited_num_ids = []
        for root_list_item in first_root_list_items:
            if root_list_item.num_id in visited_num_ids:
                continue
            visited_num_ids.append(root_list_item.num_id)
            lst_style = get_list_style(
                self.numbering_root,
                root_list_item.num_id.num_id,
                root_list_item.ilvl,
            )
            if lst_style != 'upperRoman':
                continue
            ilvl = min(
                el.ilvl for el in body.find_all('p')
                if el.num_id == root_list_item.num_id
            )
            root_upper_roman_list_items = [
                el for el in body.find_all('p')
                if el.num_id == root_list_item.num_id and
                el.ilvl == ilvl
            ]
            for list_item in root_upper_roman_list_items:
                element_meta_data[list_item]['is_list_item'] = False
                element_meta_data[list_item]['is_first_list_item'] = False
                element_meta_data[list_item]['is_last_list_item_in_root'] = False  # noqa

                element_meta_data[list_item]['heading_level'] = UPPER_ROMAN_TO_HEADING_VALUE  # noqa

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
                        element_meta_data[children[i]]['next'] = children[i + 1]  # noqa
                except IndexError:
                    pass
                try:
                    if children[i - 1] is not None:
                        element_meta_data[children[i]]['previous'] = children[i - 1]  # noqa
                except IndexError:
                    pass
        # Assign next for everything in the root.
        _assign_next(_get_children_with_content(body))

        # In addition set next for everything in table cells.
        for tc in body.find_all('tc'):
            _assign_next(_get_children_with_content(tc))

    def _init(
            self,
            add_attributes=False,
            convert_root_level_upper_roman=False,
            styles_dict=None,
            numbering_root=None,
            *args,
            **kwargs):
        super(PydocxLXMLParser, self)._init(*args, **kwargs)
        if add_attributes:
            self.convert_root_level_upper_roman = convert_root_level_upper_roman  # noqa
            self.styles_dict = styles_dict
            self.numbering_root = numbering_root
            self._set_list_attributes(self)
            self._set_table_attributes(self)
            self._set_is_in_table(self)

            list_elements = [
                child for child in self.find_all('p')
                if child.is_list_item
            ]
            num_ids = set([i.num_id for i in list_elements])
            ilvls = set([i.ilvl for i in list_elements])
            self._set_first_list_item(num_ids, ilvls, list_elements)
            self._set_last_list_item(num_ids, list_elements)

            # Find the first and last li elements
            body = self.find_first('body')
            p_elements = [
                child for child in body.find_all('p')
            ]
            self._set_headers(p_elements)
            self._convert_upper_roman(body)
            self._set_next(body)


parser_lookup = etree.ElementDefaultClassLookup(element=PydocxLXMLParser)
parser = etree.XMLParser()
parser.set_element_class_lookup(parser_lookup)


def parse_xml_from_string(xml):
    return etree.fromstring(
        remove_namespaces(xml),
        parser,
    )
