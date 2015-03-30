from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import copy
import logging
import posixpath

from abc import abstractmethod, ABCMeta

from pydocx.constants import (
    EMUS_PER_PIXEL,
    INDENTATION_FIRST_LINE,
    INDENTATION_LEFT,
    INDENTATION_RIGHT,
    JUSTIFY_CENTER,
    JUSTIFY_LEFT,
    JUSTIFY_RIGHT,
    TWIPS_PER_POINT,
)
from pydocx.exceptions import MalformedDocxException
from pydocx.managers.styles import StylesManager
from pydocx.models.styles import (
    ParagraphProperties,
    RunProperties,
)
from pydocx.util.memoize import MulitMemoizeMixin
from pydocx.util.preprocessor import PydocxPreProcessor
from pydocx.util.uri import uri_is_external
from pydocx.util.xml import (
    find_all,
    find_ancestor_with_tag,
    find_first,
    get_list_style,
    has_descendant_with_tag,
)
from pydocx.wordml import WordprocessingDocument

logger = logging.getLogger("NewParser")


class IterativeXmlParser(object):
    '''
    The IterativeXmlParser is an abstract class for parsing/processing each
    level of an XML data source.

    `visited` may optionally be passed in as an external object for keeping
    track of elements that have been processed. If not passed in, this class
    maintains its own list of visited elements.

    To be useful, this class must be subclassed to override the
    `process_tag_completion` method.
    '''

    def __init__(self, visited=None):
        self.visited = visited
        if self.visited is None:
            self.visited = set()

    def process_tag_completion(self, result_stack, element, stack):
        '''
        This handler is called when a level is completed, which means that all
        nested levels have also been completed.

        `result_stack` is a list of nested level results
        `element` is the level that is being completed
        `stack` is the stack elements above this element which are still being
        processed.
        '''
        return result_stack

    def parse(self, el):
        # A stack to preserve a child iterator, the node and the node's output
        stack = []

        # A stack to preserve the output generated at the current node level.
        # This stack gets joined together and pushed onto the parent node's
        # stack when a level is finished
        result_stack = []

        # An iterator over the node's children
        current_iter = iter([el])
        while True:
            next_item = None
            try:
                next_item = next(current_iter)
            except StopIteration:
                # If this happens it means that there are no more children in
                # this node
                pass

            if next_item is None:
                # There are no more children in this node, so we need to jump
                # back to the parent node and render it
                if stack:
                    parent = stack.pop()
                    current_iter = parent['iterator']
                    result = self.process_tag_completion(
                        result_stack,
                        parent['element'],
                        stack,
                    )
                    if result:
                        parent['result'].append(result)
                    result_stack = parent['result']
                else:
                    # There are no more parent nodes, we're done
                    break
            elif next_item not in self.visited:
                self.visited.add(next_item)
                stack.append({
                    'element': next_item,
                    'iterator': current_iter,
                    'result': result_stack,
                })
                result_stack = []
                current_iter = iter(next_item)
        return result_stack


class TagEvaluatorStringJoinedIterativeXmlParser(IterativeXmlParser):
    '''
    An IterativeXmlParser that uses a tag-evaluating mechanism for evaluating
    results at each tag level.
    `tag_evaluator_mapping` is a dictionary consisting of the tag name as the
    key, and the handler as the value.

    When a tag is encountered, the handler is called. The handler must accept
    three parameters: the element itself, the current result, and the parent
    stack of elements.
    '''

    def __init__(self, tag_evaluator_mapping, visited=None):
        super(TagEvaluatorStringJoinedIterativeXmlParser, self).__init__(
            visited=visited,
        )
        self.tag_evaluator_mapping = tag_evaluator_mapping

    def parse(self, el):
        result = super(TagEvaluatorStringJoinedIterativeXmlParser, self).parse(
            el,
        )
        return ''.join(result)

    def process_tag_completion(self, result_stack, element, stack):
        result = ''.join(result_stack)
        func = self.tag_evaluator_mapping.get(element.tag)
        if callable(func):
            result = func(element, result, stack)
        return result


class DocxParser(MulitMemoizeMixin):
    __metaclass__ = ABCMeta
    pre_processor_class = PydocxPreProcessor

    def __init__(
        self,
        path,
        convert_root_level_upper_roman=False,
    ):
        self.path = path
        self._parsed = ''
        self.block_text = ''
        self.page_width = 0
        self.convert_root_level_upper_roman = convert_root_level_upper_roman
        self.pre_processor = None
        self.visited = set()
        self.list_depth = 0
        self.footnote_index = 1
        self.footnote_ordering = []
        self.current_part = None

        self.parse_tag_evaluator_mapping = {
            'br': self.parse_break_tag,
            'delText': self.parse_deletion,
            'drawing': self.parse_image,
            'footnoteReference': self.parse_footnote_reference,
            'footnoteRef': self.parse_footnote_ref,
            'hyperlink': self.parse_hyperlink,
            'ins': self.parse_insertion,
            'noBreakHyphen': self.parse_hyphen,
            'pict': self.parse_image,
            'pPr': self.parse_paragraph_properties,
            'p': self.parse_p,
            'r': self.parse_r,
            'rPr': self.parse_run_properties,
            'tab': self.parse_tab,
            'tbl': self.parse_table,
            'tc': self.parse_table_cell,
            'tr': self.parse_table_row,
            't': self.parse_t,
        }
        self.parser = TagEvaluatorStringJoinedIterativeXmlParser(
            tag_evaluator_mapping=self.parse_tag_evaluator_mapping,
            visited=self.visited,
        )

    def parse_run_properties(self, el, parsed, stack):
        properties = RunProperties.load(el)
        parent = stack[-1]['element']
        self.styles_manager.save_properties_for_element(parent, properties)

    def parse_paragraph_properties(self, el, parsed, stack):
        properties = ParagraphProperties.load(el)
        parent = stack[-1]['element']
        self.styles_manager.save_properties_for_element(parent, properties)

    def _load(self):
        self.document = WordprocessingDocument(path=self.path)
        main_document_part = self.document.main_document_part
        if main_document_part is None:
            raise MalformedDocxException

        self.numbering_root = None
        numbering_part = main_document_part.numbering_definitions_part
        if numbering_part:
            self.numbering_root = numbering_part.root_element

        self.page_width = self._get_page_width(main_document_part.root_element)
        self.styles_manager = StylesManager(
            main_document_part.style_definitions_part,
        )
        self.styles = self.styles_manager.styles
        self.parse_begin(main_document_part)

    def load_footnotes(self, main_document_part):
        footnotes = {}
        if not main_document_part:
            return footnotes
        if not main_document_part.footnotes_part:
            return footnotes
        if not main_document_part.footnotes_part.root_element:
            return footnotes
        self.current_part = main_document_part.footnotes_part
        for element in main_document_part.footnotes_part.root_element:
            if element.tag == 'footnote':
                footnote_id = element.get('id')
                footnotes[footnote_id] = self.parse(element)
        return footnotes

    def parse_begin(self, main_document_part):
        self.populate_memoization({
            'find_all': find_all,
            'find_first': find_first,
            'has_descendant_with_tag': has_descendant_with_tag,
            '_get_tcs_in_column': self._get_tcs_in_column,
        })

        self.pre_processor = self.pre_processor_class(
            convert_root_level_upper_roman=self.convert_root_level_upper_roman,
            styles=self.styles,
            numbering_root=self.numbering_root,
        )
        self.pre_processor.perform_pre_processing(main_document_part.root_element)  # noqa

        self.footnote_id_to_content = self.load_footnotes(main_document_part)

        self.current_part = main_document_part
        self._parsed = self.parse(main_document_part.root_element)

    def parse(self, el):
        return self.parser.parse(el)

    def _get_page_width(self, root_element):
        pgSzEl = find_first(root_element, 'pgSz')
        if pgSzEl is not None:
            # pgSz is defined in twips, convert to points
            pgSz = int(float(pgSzEl.attrib['w']))
            return pgSz / TWIPS_PER_POINT

    def parse_footnote_ref(self, el, text, stack):
        footnote_id = None
        for item in reversed(stack):
            if item['element'].tag == 'footnote':
                footnote_id = item['element'].get('id')
                break
        return self.footnote_ref(footnote_id)

    def parse_footnote_reference(self, el, text, stack):
        footnote_id = el.get('id')
        if footnote_id not in self.footnote_id_to_content:
            return ''
        self.footnote_ordering.append(footnote_id)
        index = self.footnote_index
        self.footnote_index += 1
        return self.footnote_reference(footnote_id, index)

    def parse_page_break(self, el, text, stack):
        # TODO figure out what parsed is getting overwritten
        return self.page_break()

    def parse_table(self, el, text, stack):
        return self.table(text)

    def parse_table_row(self, el, text, stack):
        return self.table_row(text)

    def parse_table_cell(self, el, text, stack):
        v_merge = find_first(el, 'vMerge')
        if v_merge is not None and (
                'restart' != v_merge.get('val', '')):
            return ''
        colspan = self.get_colspan(el)
        rowspan = self._get_rowspan(el, v_merge)
        if rowspan > 1:
            rowspan = str(rowspan)
        else:
            rowspan = ''
        return self.table_cell(text, colspan, rowspan)

    def parse_list(self, el, text, stack):
        """
        All the meat of building the list is done in _parse_list, however we
        call this method for two reasons: It is the naming convention we are
        following. And we need a reliable way to raise and lower the list_depth
        (which is used to determine if we are in a list). I could have done
        this in _parse_list, however it seemed cleaner to do it here.
        """
        self.list_depth += 1
        parsed = self._parse_list(el, text, stack)
        self.list_depth -= 1
        if self.pre_processor.is_in_table(el):
            return self.parse_table_cell_contents(el, parsed, stack)
        return parsed

    def get_list_style(self, num_id, ilvl):
        return get_list_style(self.numbering_root, num_id, ilvl)

    def _build_list(self, el, text):
        # Get the list style for the pending list.
        list_style = self.get_list_style(
            self.pre_processor.num_id(el).num_id,
            self.pre_processor.ilvl(el),
        )

        parsed = text
        # Create the actual list and return it.
        if list_style == 'bullet':
            return self.unordered_list(parsed)
        else:
            return self.ordered_list(
                parsed,
                list_style,
            )

    def _parse_list(self, el, text, stack):
        parsed = self.parse_list_item(el, text, stack)
        num_id = self.pre_processor.num_id(el)
        ilvl = self.pre_processor.ilvl(el)
        # Everything after this point assumes the first element is not also the
        # last. If the first element is also the last then early return by
        # building and returning the completed list.
        if self.pre_processor.is_last_list_item_in_root(el):
            return self._build_list(el, parsed)
        next_el = self.pre_processor.next(el)

        def is_same_list(next_el, num_id, ilvl):
            # Bail if next_el is not an element
            if next_el is None:
                return False
            if self.pre_processor.is_last_list_item_in_root(next_el):
                return False
            # If next_el is not a list item then roll it into the list by
            # returning True.
            if not self.pre_processor.is_list_item(next_el):
                return True
            if self.pre_processor.num_id(next_el) != num_id:
                # The next element is a new list entirely
                return False
            if int(self.pre_processor.ilvl(next_el)) < int(ilvl):
                # The next element is de-indented, so this is really the last
                # element in the list
                return False
            return True

        while is_same_list(next_el, num_id, ilvl):
            if next_el in self.visited:
                # Early continue for elements we have already visited.
                next_el = self.pre_processor.next(next_el)
                continue

            if self.pre_processor.is_list_item(next_el):
                # Reset the ilvl
                ilvl = self.pre_processor.ilvl(next_el)

            parsed += self.parse(next_el)
            next_el = self.pre_processor.next(next_el)

        def should_parse_last_el(last_el, first_el):
            if last_el is None:
                return False
            # Different list
            if (
                    self.pre_processor.num_id(last_el) !=
                    self.pre_processor.num_id(first_el)):
                return False
            # Will be handled when the ilvls do match (nesting issue)
            if (
                    self.pre_processor.ilvl(last_el) !=
                    self.pre_processor.ilvl(first_el)):
                return False
            # We only care about last items that have not been parsed before
            # (first list items are always parsed at the beginning of this
            # method.)
            return (
                not self.pre_processor.is_first_list_item(last_el) and
                self.pre_processor.is_last_list_item_in_root(last_el)
            )
        if should_parse_last_el(next_el, el):
            parsed += self.parse(next_el)

        # If the list has no content, then we don't need to worry about the
        # list styling, because it will be stripped out.
        if parsed == '':
            return parsed

        return self._build_list(el, parsed)

    def justification(self, el, text):
        paragraph_tag_property = el.find('pPr')
        if paragraph_tag_property is None:
            return text

        jc = paragraph_tag_property.find('jc')
        indentation = paragraph_tag_property.find('ind')
        if jc is None and indentation is None:
            return text
        alignment = None
        right = None
        left = None
        firstLine = None
        if jc is not None:  # text alignments
            value = jc.attrib['val']
            if value in [JUSTIFY_LEFT, JUSTIFY_CENTER, JUSTIFY_RIGHT]:
                alignment = value

        if indentation is not None:
            if INDENTATION_RIGHT in indentation.attrib:
                right = int(indentation.attrib[INDENTATION_RIGHT])
            if INDENTATION_LEFT in indentation.attrib:
                left = int(indentation.attrib[INDENTATION_LEFT])
            if INDENTATION_FIRST_LINE in indentation.attrib:
                firstLine = int(indentation.attrib[INDENTATION_FIRST_LINE])
        if any([alignment, firstLine, left, right]):
            return self.indent(text, alignment, firstLine, left, right)
        return text

    def parse_p(self, el, text, stack):
        if text == '':
            return ''
        # TODO This is still not correct, however it fixes the bug. We need to
        # apply the classes/styles on p, td, li and h tags instead of inline,
        # but that is for another ticket.
        text = self.justification(el, text)
        if self.pre_processor.is_first_list_item(el):
            return self.parse_list(el, text, stack)
        if self.pre_processor.heading_level(el):
            return self.parse_heading(el, text, stack)
        if self.pre_processor.is_list_item(el):
            return self.parse_list_item(el, text, stack)
        if self.pre_processor.is_in_table(el):
            return self.parse_table_cell_contents(el, text, stack)
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
        if self.pre_processor.is_list_item(next_el):
            return False
        if self.pre_processor.previous(next_el) is None:
            return False
        tag_is_inline_like = any(
            self.memod_tree_op('has_descendant_with_tag', next_el, tag) for
            tag in inline_like_tags
        )
        if tag_is_inline_like:
            return False
        if (
                self.pre_processor.is_last_list_item_in_root(
                    self.pre_processor.previous(next_el))):
            return False
        if self.pre_processor.previous(next_el).tag not in paragraph_like_tags:
            return False
        if next_el.tag not in paragraph_like_tags:
            return False
        return True

    def parse_heading(self, el, parsed, stack):
        return self.heading(parsed, self.pre_processor.heading_level(el))

    def parse_list_item(self, el, text, stack):
        # If for whatever reason we are not currently in a list, then start
        # a list here. This will only happen if the num_id/ilvl combinations
        # between lists is not well formed.
        parsed = text
        if self.list_depth == 0:
            return self.parse_list(el, parsed, stack)

        def _should_parse_next_as_content(el):
            """
            Get the contents of the next el and append it to the
            contents of the current el (that way things like tables
            are actually in the li tag instead of in the ol/ul tag).
            """
            next_el = self.pre_processor.next(el)
            if next_el is None:
                return False
            if (
                    not self.pre_processor.is_list_item(next_el) and
                    not self.pre_processor.is_last_list_item_in_root(el)
            ):
                return True
            if self.pre_processor.is_first_list_item(next_el):
                if (
                        int(self.pre_processor.ilvl(next_el)) <=
                        int(self.pre_processor.ilvl(el) or 0)):
                    return False
                if (
                        self.pre_processor.num_id(next_el) ==
                        self.pre_processor.num_id(el)):
                    return True
            return False

        while el is not None:
            if _should_parse_next_as_content(el):
                el = self.pre_processor.next(el)
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

    def _get_tcs_in_column(self, tbl, column_index):
        return [
            tc for tc in self.memod_tree_op('find_all', tbl, 'tc')
            if self.pre_processor.column_index(tc) == column_index
        ]

    def _get_rowspan(self, el, v_merge):
        restart_in_v_merge = False
        if v_merge is not None and 'val' in v_merge.attrib:
            restart_in_v_merge = 'restart' in v_merge.attrib['val']

        if not restart_in_v_merge:
            return -1

        current_row = self.pre_processor.row_index(el)
        current_col = self.pre_processor.column_index(el)
        rowspan = 1
        result = -1
        tbl = find_ancestor_with_tag(self.pre_processor, el, 'tbl')
        # We only want table cells that have a higher row_index that is greater
        # than the current_row and that are on the current_col
        if tbl is None:
            return -1

        tcs = [
            tc for tc in self.memod_tree_op(
                '_get_tcs_in_column', tbl, current_col,
            ) if self.pre_processor.row_index(tc) >= current_row
        ]

        def should_increment_rowspan(tc):
            if not self.pre_processor.vmerge_continue(tc):
                return False
            return True

        for tc in tcs:
            if should_increment_rowspan(tc):
                rowspan += 1
            else:
                rowspan = 1
            if rowspan > 1:
                result = rowspan
        return result

    def get_colspan(self, el):
        grid_span = find_first(el, 'gridSpan')
        if grid_span is None:
            return ''
        return grid_span.attrib['val']

    def parse_table_cell_contents(self, el, text, stack):
        parsed = text

        next_el = self.pre_processor.next(el)
        if next_el is not None:
            if self._should_append_break_tag(next_el):
                parsed += self.break_tag()
        return parsed

    def parse_hyperlink(self, el, text, stack):
        relationship_id = el.get('id')
        package_part = self.current_part.package_part
        try:
            relationship = package_part.get_relationship(
                relationship_id=relationship_id,
            )
        except KeyError:
            # Preserve the text even if we are unable to resolve the hyperlink
            return text
        href = self.escape(relationship.target_uri)
        return self.hyperlink(text, href)

    def _get_image_id(self, el):
        # Drawings
        blip = find_first(el, 'blip')
        if blip is not None:
            # On drawing tags the id is actually whatever is returned from the
            # embed attribute on the blip tag. Thanks a lot Microsoft.
            r_id = blip.get('embed')
            if r_id is None:
                r_id = blip.get('link')
            return r_id
        # Picts
        imagedata = find_first(el, 'imagedata')
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
        sizes = el.find('./*/graphic/graphicData/pic/spPr/xfrm/ext')
        if sizes is not None and sizes.get('cx'):
            if sizes.get('cx'):
                x = self._convert_image_size(int(sizes.get('cx')))
            if sizes.get('cy'):
                y = self._convert_image_size(int(sizes.get('cy')))
            return (
                '%dpx' % x,
                '%dpx' % y,
            )
        shape = find_first(el, 'shape')
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

    def parse_image(self, el, parsed, stack):
        x, y = self._get_image_size(el)
        relationship_id = self._get_image_id(el)
        try:
            image_part = self.current_part.get_part_by_id(
                relationship_id=relationship_id,
            )
            is_uri_external = uri_is_external(image_part.uri)
            if is_uri_external:
                data = image_part.uri
            else:
                data = image_part.stream.read()
        except KeyError:
            return ''
        _, filename = posixpath.split(image_part.uri)
        return self.image(
            data,
            filename,
            x,
            y,
            uri_is_external=is_uri_external,
        )

    def parse_t(self, el, parsed, stack):
        if el.text is None:
            return ''
        return self.escape(el.text)

    def parse_tab(self, el, parsed, stack):
        return self.tab()

    def parse_hyphen(self, el, parsed, stack):
        return '-'

    def parse_break_tag(self, el, parsed, stack):
        if el.attrib.get('type') == 'page':
            return self.parse_page_break(el, parsed, stack)
        return self.break_tag()

    def parse_deletion(self, el, parsed, stack):
        if el.text is None:
            return ''
        return self.deletion(el.text, '', '')

    def parse_insertion(self, el, parsed, stack):
        return self.insertion(parsed, '', '')

    def parse_r(self, el, text, stack):
        """
        Parse the running text.
        """
        if not text:
            return ''

        properties = self.styles_manager.get_resolved_properties_for_element(
            el,
            stack,
        )

        def get_properties_with_no_font_size():
            # Only set paragraph_properties if properties has a size.
            if not properties.size:
                return
            copied_el = copy.deepcopy(el)
            rpr = copied_el.find('./rPr')
            if rpr is None:
                return

            size_tag = rpr.find('./sz')
            if size_tag is None:
                return

            rpr.remove(size_tag)

            return self.styles_manager.get_resolved_properties_for_element(
                copied_el,
                stack,
            )

        paragraph_properties = get_properties_with_no_font_size()

        def is_local_size_smaller():
            # If paragraph_properties is None then the size was not set
            # (meaning it can't be bigger or smaller than the default for the
            # paragraph, so early exit.
            if paragraph_properties is None:
                return False
            if paragraph_properties.size is None:
                return False
            return properties.size < paragraph_properties.size

        styles_needing_application = []

        property_rules = [
            (properties.bold, True, self.bold),
            (properties.italic, True, self.italics),
            (properties.underline, True, self.underline),
            (properties.caps, True, self.caps),
            (properties.small_caps, True, self.small_caps),
            (properties.strike, True, self.strike),
            (properties.dstrike, True, self.strike),
            (properties.vanish, True, self.hide),
            (properties.hidden, True, self.hide),
            (properties.vertical_align, 'superscript', self.superscript),
            (properties.vertical_align, 'subscript', self.subscript),
        ]
        for actual_value, enabled_value, handler in property_rules:
            if enabled_value is True and actual_value or (
                    actual_value == enabled_value):
                styles_needing_application.append(handler)

        if self.underline in styles_needing_application:
            for item in stack:
                # If we're handling a hyperlink, disable underline styling
                if item['element'].tag == 'hyperlink':
                    styles_needing_application.remove(self.underline)
                    break

        # Lets try to deal with faked superscript/subscript tags by checking
        # the position.
        def handle_faked_sup_and_sub_tags():
            if not is_local_size_smaller():
                return
            if not properties.position:
                return
            if self.subscript in styles_needing_application:
                return
            if self.superscript in styles_needing_application:
                return
            if properties.position > 0:
                styles_needing_application.append(self.superscript)
            else:
                styles_needing_application.append(self.subscript)
        handle_faked_sup_and_sub_tags()

        # Apply all the handlers.
        for func in styles_needing_application:
            text = func(text)

        return text

    @property
    def parsed(self):
        if not self._parsed:
            self._load()
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
    def image_handler(self, image_data, path, uri_is_external):
        return path

    @abstractmethod
    def image(self, data, filename, x, y, uri_is_external):
        return self.image_handler(data, filename, uri_is_external)

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
    def caps(self, text):
        return text

    @abstractmethod
    def small_caps(self, text):
        return text

    @abstractmethod
    def strike(self, text):
        return text

    @abstractmethod
    def hide(self, text):
        return text

    @abstractmethod
    def superscript(self, text):
        return text

    @abstractmethod
    def subscript(self, text):
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
    def indent(
        self,
        text,
        alignment=None,
        left=None,
        right=None,
        firstLine=None,
    ):
        return text
