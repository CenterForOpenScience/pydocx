# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import posixpath
import xml.sax.saxutils
from collections import namedtuple

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
from pydocx.openxml import wordprocessing
from pydocx.openxml.wordprocessing import (
    ParagraphProperties,
    RunProperties,
)
from pydocx.util.memoize import MultiMemoizeMixin
from pydocx.util.preprocessor import PydocxPreProcessor
from pydocx.util.uri import uri_is_external
from pydocx.util.xml import (
    find_all,
    find_ancestor_with_tag,
    get_list_style,
    has_descendant_with_tag,
)
from pydocx.openxml.packaging import WordprocessingDocument

logger = logging.getLogger("NewParser")


class PyDocXExporter(object):
    def __init__(self, path):
        self.path = path
        self._document = None
        # TODO each XmlModel should be self-aware of its container
        self._page_width = None
        self.previous = {}

        self.node_type_to_export_func_map = {
            wordprocessing.Document: self.export_document,
            wordprocessing.Body: self.export_body,
            wordprocessing.Paragraph: self.export_paragraph,
            wordprocessing.Run: self.export_run,
            wordprocessing.Text: self.export_text,
            wordprocessing.Hyperlink: self.export_hyperlink,
            wordprocessing.Break: self.export_break,
            wordprocessing.NoBreakHyphen: self.export_no_break_hyphen,
            wordprocessing.Table: self.export_table,
            wordprocessing.TableRow: self.export_table_row,
            wordprocessing.TableCell: self.export_table_cell,
            wordprocessing.Drawing: self.export_drawing,
            wordprocessing.SmartTagRun: self.export_smart_tag_run,
            wordprocessing.InsertedRun: self.export_inserted_run,
        }

    @property
    def document(self):
        if not self._document:
            self.document = self.load_document()
        return self._document

    @document.setter
    def document(self, document):
        self._document = document

    def load_document(self):
        self.document = WordprocessingDocument(path=self.path)
        return self.document

    @property
    def main_document_part(self):
        return self.document.main_document_part

    @property
    def style_definitions_part(self):
        if self.main_document_part:
            return self.main_document_part.style_definitions_part

    @property
    def numbering_definitions_part(self):
        if self.main_document_part:
            return self.main_document_part.numbering_definitions_part

    @property
    def parsed(self):
        if self.main_document_part is None:
            raise MalformedDocxException
        return self.export()

    def export(self):
        document = self.main_document_part.document
        if document:
            for result in self.export_node(document):
                yield result

    def export_node(self, node):
        for node_type, caller in self.node_type_to_export_func_map.items():
            if isinstance(node, node_type):
                for result in caller(node):
                    yield result
                break

    @property
    def page_width(self):
        if self._page_width is None:
            page_width = self.calculate_page_width()
            if page_width is None:
                page_width = 0
            self._page_width = page_width
        return self._page_width

    def calculate_page_width(self):
        document = self.main_document_part.document
        try:
            page_size = document.body.final_section_properties.page_size
        except AttributeError:
            page_size = None
        if page_size:
            width = page_size.get('w')
            if not width:
                return
            try:
                width = int(float(width))
            except ValueError:
                return
            # pgSz is defined in twips, convert to points
            return width / TWIPS_PER_POINT

    def export_document(self, document):
        return self.export_node(document.body)

    # TODO not a fan of this name
    def yield_nested(self, iterable, func):
        previous = None
        for item in iterable:
            # TODO better name / structure for this.
            self.previous[item.parent] = previous
            for result in func(item):
                yield result
            previous = item

    def export_body(self, body):
        return self.yield_nested(body.children, self.export_node)

    def export_paragraph(self, paragraph):
        results = self.yield_nested(paragraph.children, self.export_node)
        if paragraph.effective_properties:
            results = self.export_paragraph_apply_properties(paragraph, results)  # noqa
        return results

    def get_paragraph_styles_to_apply(self, paragraph):
        properties = paragraph.effective_properties
        property_rules = [
            (properties.justification, self.export_paragraph_property_justification),  # noqa
            (properties.indentation, self.export_paragraph_property_indentation),  # noqa
        ]
        for actual_value, handler in property_rules:
            if actual_value:
                yield handler

    def export_paragraph_property_justification(self, paragraph, results):
        return results

    def export_paragraph_property_indentation(self, paragraph, results):
        return results

    def export_paragraph_apply_properties(self, paragraph, results):
        styles_to_apply = self.get_paragraph_styles_to_apply(paragraph)
        for func in styles_to_apply:
            results = func(paragraph, results)
        return results

    def export_break(self, br):
        raise StopIteration

    def export_run(self, run):
        results = self.yield_nested(run.children, self.export_node)
        if run.effective_properties:
            results = self.export_run_apply_properties(run, results)
        return results

    def get_run_styles_to_apply(self, run):
        properties = run.effective_properties
        property_rules = [
            (properties.bold, self.export_run_property_bold),
            (properties.italic, self.export_run_property_italic),
            (properties.underline, self.export_run_property_underline),
            (properties.caps, self.export_run_property_caps),
            (properties.small_caps, self.export_run_property_small_caps),
            (properties.strike, self.export_run_property_strike),
            (properties.dstrike, self.export_run_property_dstrike),
            (properties.vanish, self.export_run_property_vanish),
            (properties.hidden, self.export_run_property_hidden),
            (properties.vertical_align, self.export_run_property_vertical_align),  # noqa
        ]
        for actual_value, handler in property_rules:
            if actual_value:
                yield handler

    def export_run_apply_properties(self, run, results):
        styles_to_apply = self.get_run_styles_to_apply(run)
        for func in styles_to_apply:
            results = func(run, results)
        return results

    def export_run_property_bold(self, run, results):
        return results

    def export_run_property_italic(self, run, results):
        return results

    def export_run_property_underline(self, run, results):
        return results

    def export_run_property_caps(self, run, results):
        return results

    def export_run_property_small_caps(self, run, results):
        return results

    def export_run_property_strike(self, run, results):
        return results

    def export_run_property_dstrike(self, run, results):
        return results

    def export_run_property_vanish(self, run, results):
        return results

    def export_run_property_hidden(self, run, results):
        return results

    def export_run_property_vertical_align(self, run, results):
        return results

    def export_hyperlink(self, hyperlink):
        return self.yield_nested(hyperlink.children, self.export_node)

    def export_text(self, text):
        if not text.text:
            yield ''
        else:
            yield self.escape(text.text)

    def export_no_break_hyphen(self, hyphen):
        yield '-'

    def export_table(self, table):
        return self.yield_nested(table.rows, self.export_node)

    def export_table_row(self, table_row):
        return self.yield_nested(table_row.cells, self.export_node)

    def export_table_cell(self, table_cell):
        return self.yield_nested(table_cell.children, self.export_node)

    def escape(self, text):
        return xml.sax.saxutils.quoteattr(text)[1:-1]

    def export_drawing(self, drawing):
        raise StopIteration

    def export_smart_tag_run(self, smart_tag):
        return self.yield_nested(smart_tag.children, self.export_node)

    def export_inserted_run(self, inserted_run):
        return self.yield_nested(inserted_run.children, self.export_node)


ParserContext = namedtuple(
    'ParserContext',
    [
        'element',
        'parsed_result',
        'stack',
        'next_element',
    ],
)

ParserStack = namedtuple(
    'ParserStack',
    [
        'element',
        'iterator',
        'parsed_result',
        'next_element',
    ],
)


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

    def process_tag_completion(self, context):
        '''
        This handler is called when a level is completed, which means that all
        nested levels have also been completed.

        `context` is a ParserContext instance
        '''
        return context.parsed_result

    def get_context(self, element, parsed_result, stack, next_element):
        return ParserContext(
            element=element,
            parsed_result=parsed_result,
            stack=stack,
            next_element=next_element,
        )

    def parse(self, el):
        # A stack to preserve a child iterator, the node and the node's output
        stack = []

        # A list to preserve the output generated at the current node level.
        # This list gets joined together and pushed onto the parent node's
        # parsed output list when a level is finished
        parsed_result = []

        # An iterator over the node's children
        current_iter = iter([el])
        next_item = None
        while True:
            current_item = next_item
            try:
                next_item = next(current_iter)
                if next_item is not None and current_item is None:
                    continue
            except StopIteration:
                # If this happens it means that there are no more children in
                # this node
                next_item = None

            if current_item is None:
                # There are no more children in this node, so we need to jump
                # back to the parent node and render it
                if stack:
                    parent = stack.pop()
                    current_iter = parent.iterator
                    context = self.get_context(
                        element=parent.element,
                        parsed_result=parsed_result,
                        stack=stack,
                        next_element=next_item,
                    )
                    current_level_result = self.process_tag_completion(context)
                    if current_level_result:
                        parent.parsed_result.append(current_level_result)
                    parsed_result = parent.parsed_result
                    next_item = parent.next_element
                else:
                    # There are no more parent nodes, we're done
                    break
            elif current_item not in self.visited:
                self.visited.add(current_item)
                stack.append(ParserStack(
                    element=current_item,
                    iterator=current_iter,
                    parsed_result=parsed_result,
                    next_element=next_item,
                ))
                parsed_result = []
                current_iter = iter(current_item)
                next_item = None
        return parsed_result


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

    def get_context(self, element, parsed_result, stack, next_element):
        parsed_result = ''.join(parsed_result)
        return super(
            TagEvaluatorStringJoinedIterativeXmlParser,
            self,
        ).get_context(
            element=element,
            parsed_result=parsed_result,
            stack=stack,
            next_element=next_element,
        )

    def process_tag_completion(self, context):
        func = self.tag_evaluator_mapping.get(context.element.tag)
        next_in_line = super(TagEvaluatorStringJoinedIterativeXmlParser, self)
        parsed_result = next_in_line.process_tag_completion(context)
        if callable(func):
            parsed_result = func(context)
        return parsed_result


class OldPyDocXExporter(MultiMemoizeMixin):
    __metaclass__ = ABCMeta
    pre_processor_class = PydocxPreProcessor

    def __init__(self, path):
        self.path = path
        self._parsed = ''
        self.block_text = ''
        self.page_width = 0
        self.pre_processor = None
        self.visited = set()
        self.list_depth = 0
        self.footnote_index = 1
        self.footnote_ordering = []
        self.current_part = None

        self._document = None

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

    def _has_direct_parent(self, stack, tag_name):
        return stack and stack[-1].element.tag == tag_name

    def _get_page_width(self, root_element):
        pgSzEl = root_element.find('./body/sectPr/pgSz')
        if pgSzEl is not None:
            # pgSz is defined in twips, convert to points
            pgSz = int(float(pgSzEl.attrib['w']))
            return pgSz / TWIPS_PER_POINT

    def get_effective_properties(self, context):
        return self.style_definitions_part.get_resolved_properties_for_element(
            context.element,
            context.stack,
        )

    def get_local_properties(self, context):
        return self.style_definitions_part.properties_for_elements.get(context.element)  # noqa

    def parse_run_properties(self, context):
        properties = RunProperties.load(context.element)
        parent = context.stack[-1].element
        self.style_definitions_part.save_properties_for_element(parent, properties)  # noqa

    def parse_paragraph_properties(self, context):
        properties = ParagraphProperties.load(context.element)
        parent = context.stack[-1].element
        self.style_definitions_part.save_properties_for_element(parent, properties)  # noqa

    @property
    def document(self):
        if not self._document:
            self.document = self.load_document()
        return self._document

    @document.setter
    def document(self, document):
        self._document = document

    def load_document(self):
        self.document = WordprocessingDocument(path=self.path)
        return self.document

    @property
    def main_document_part(self):
        return self.document.main_document_part

    @property
    def style_definitions_part(self):
        if self.main_document_part:
            return self.main_document_part.style_definitions_part

    @property
    def numbering_definitions_part(self):
        if self.main_document_part:
            return self.main_document_part.numbering_definitions_part

    def _load(self):
        if self.main_document_part is None:
            raise MalformedDocxException

        self.numbering_root = None
        if self.numbering_definitions_part:
            self.numbering_root = self.numbering_definitions_part.root_element

        self.page_width = self._get_page_width(self.main_document_part.root_element)  # noqa
        self.parse_begin(self.main_document_part)

    def load_footnotes(self, main_document_part):
        footnotes = {}
        if not main_document_part:
            return footnotes
        if not main_document_part.footnotes_part:
            return footnotes
        if main_document_part.footnotes_part.root_element is None:
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
            'has_descendant_with_tag': has_descendant_with_tag,
            '_get_tcs_in_column': self._get_tcs_in_column,
        })

        self.pre_processor = self.pre_processor_class(
            numbering_root=self.numbering_root,
        )
        self.pre_processor.perform_pre_processing(main_document_part.root_element)  # noqa

        self.footnote_id_to_content = self.load_footnotes(main_document_part)

        self.current_part = main_document_part
        self._parsed = self.parse(main_document_part.root_element)

    def parse(self, el):
        return self.parser.parse(el)

    def parse_footnote_ref(self, context):
        footnote_id = None
        for item in reversed(context.stack):
            if item.element.tag == 'footnote':
                footnote_id = item.element.get('id')
                break
        return self.footnote_ref(footnote_id)

    def parse_footnote_reference(self, context):
        footnote_id = context.element.get('id')
        if footnote_id not in self.footnote_id_to_content:
            return ''
        self.footnote_ordering.append(footnote_id)
        index = self.footnote_index
        self.footnote_index += 1
        return self.footnote_reference(footnote_id, index)

    def parse_page_break(self, context):
        # TODO figure out what parsed is getting overwritten
        return self.page_break()

    def parse_table(self, context):
        return self.table(context.parsed_result)

    def parse_table_row(self, context):
        return self.table_row(context.parsed_result)

    def parse_table_cell(self, context):
        v_merge = context.element.find('./tcPr/vMerge')
        if v_merge is not None and (
                'restart' != v_merge.get('val', '')):
            return ''
        colspan = self.get_colspan(context.element)
        rowspan = self._get_rowspan(context.element, v_merge)
        if rowspan > 1:
            rowspan = str(rowspan)
        else:
            rowspan = ''
        return self.table_cell(context.parsed_result, colspan, rowspan)

    def parse_list(self, context):
        """
        All the meat of building the list is done in _parse_list, however we
        call this method for two reasons: It is the naming convention we are
        following. And we need a reliable way to raise and lower the list_depth
        (which is used to determine if we are in a list). I could have done
        this in _parse_list, however it seemed cleaner to do it here.
        """
        self.list_depth += 1
        parsed = self._parse_list(context)
        self.list_depth -= 1
        if self._has_direct_parent(context.stack, 'tc'):
            context = ParserContext(
                element=context.element,
                parsed_result=parsed,
                stack=context.stack,
                next_element=context.next_element,
            )
            return self.parse_table_cell_contents(context)
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

    def _parse_list(self, context):
        parsed = self.parse_list_item(context)
        num_id = self.pre_processor.num_id(context.element)
        ilvl = self.pre_processor.ilvl(context.element)
        # Everything after this point assumes the first element is not also the
        # last. If the first element is also the last then early return by
        # building and returning the completed list.
        if self.pre_processor.is_last_list_item_in_root(context.element):
            return self._build_list(context.element, parsed)
        next_el = self.pre_processor.next(context.element)

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
        if should_parse_last_el(next_el, context.element):
            parsed += self.parse(next_el)

        # If the list has no content, then we don't need to worry about the
        # list styling, because it will be stripped out.
        if parsed == '':
            return parsed

        return self._build_list(context.element, parsed)

    def justification(self, context):
        paragraph_tag_property = context.element.find('pPr')
        if paragraph_tag_property is None:
            return context.parsed_result

        jc = paragraph_tag_property.find('jc')
        indentation = paragraph_tag_property.find('ind')
        if jc is None and indentation is None:
            return context.parsed_result
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
            return self.indent(
                context.parsed_result,
                alignment,
                firstLine,
                left,
                right,
            )
        return context.parsed_result

    def style_name_is_a_heading_level(self, style_name):
        return style_name and style_name.startswith('heading')

    def get_heading_style_name(self, context):
        properties = self.get_local_properties(context)

        parent_style = None
        if properties:
            parent_style = properties.parent_style

        styles = self.style_definitions_part.styles
        paragraph_styles = styles.get_styles_by_type('paragraph')
        style = paragraph_styles.get(parent_style)
        if style:
            style_name = style.name.lower()
            if self.style_name_is_a_heading_level(style_name):
                return style_name

    def parse_p(self, context):
        if context.parsed_result == '':
            return ''

        # TODO This is still not correct, however it fixes the bug. We need to
        # apply the classes/styles on p, td, li and h tags instead of inline,
        # but that is for another ticket.
        parsed_result = self.justification(context)
        context = ParserContext(
            element=context.element,
            parsed_result=parsed_result,
            stack=context.stack,
            next_element=context.next_element,
        )

        heading_style_name = self.get_heading_style_name(context)

        if heading_style_name:
            return self.heading(
                text=context.parsed_result,
                heading_style_name=heading_style_name,
            )

        if self.pre_processor.is_first_list_item(context.element):
            return self.parse_list(context)
        if self.pre_processor.is_list_item(context.element):
            return self.parse_list_item(context)
        if self._has_direct_parent(context.stack, 'tc'):
            return self.parse_table_cell_contents(context)
        # No p tags in li tags
        if self.list_depth == 0:
            return self.paragraph(context.parsed_result)
        return context.parsed_result

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

    def parse_list_item(self, context):
        # If for whatever reason we are not currently in a list, then start
        # a list here. This will only happen if the num_id/ilvl combinations
        # between lists is not well formed.
        parsed = context.parsed_result
        if self.list_depth == 0:
            return self.parse_list(context)

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

        el = context.element
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
            ) if self.pre_processor.row_index(tc) > current_row
        ]

        def should_increment_rowspan(tc):
            if not self.pre_processor.vmerge_continue(tc):
                return False
            return True

        for tc in tcs:
            if should_increment_rowspan(tc):
                rowspan += 1
            else:
                break

        if rowspan > 1:
            result = rowspan

        return result

    def get_colspan(self, el):
        grid_span = el.find('./tcPr/gridSpan')
        if grid_span is None:
            return ''
        return grid_span.attrib['val']

    def parse_table_cell_contents(self, context):
        parsed = context.parsed_result

        next_el = self.pre_processor.next(context.element)
        if next_el is not None:
            if self._should_append_break_tag(next_el):
                parsed += self.break_tag()
        return parsed

    def parse_hyperlink(self, context):
        relationship_id = context.element.get('id')
        package_part = self.current_part.package_part
        try:
            relationship = package_part.get_relationship(
                relationship_id=relationship_id,
            )
        except KeyError:
            # Preserve the text even if we are unable to resolve the hyperlink
            return context.parsed_result
        href = self.escape(relationship.target_uri)
        return self.hyperlink(context.parsed_result, href)

    def _get_image_id(self, el):
        # Drawings
        blip = el.find('./*/graphic/graphicData/pic/blipFill/blip')
        if blip is not None:
            # On drawing tags the id is actually whatever is returned from the
            # embed attribute on the blip tag. Thanks a lot Microsoft.
            r_id = blip.get('embed')
            if r_id is None:
                r_id = blip.get('link')
            return r_id
        # Picts
        imagedata = el.find('./shape/imagedata')
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
        shape = el.find('./shape')
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

    def parse_image(self, context):
        x, y = self._get_image_size(context.element)
        relationship_id = self._get_image_id(context.element)
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

    def parse_t(self, context):
        if context.element.text is None:
            return ''
        return self.escape(context.element.text)

    def parse_tab(self, context):
        return self.tab()

    def parse_hyphen(self, context):
        return '-'

    def parse_break_tag(self, context):
        if context.element.attrib.get('type') == 'page':
            return self.parse_page_break(context)
        return self.break_tag()

    def parse_deletion(self, context):
        if context.element.text is None:
            return ''
        return self.deletion(context.element.text, '', '')

    def parse_insertion(self, context):
        return self.insertion(context.parsed_result, '', '')

    def parse_r_determine_applicable_styles(self, context):
        properties = self.get_effective_properties(context)

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
            for item in context.stack:
                # If we're handling a hyperlink, disable underline styling
                if item.element.tag == 'hyperlink':
                    styles_needing_application.remove(self.underline)
                    break

        return styles_needing_application

    def parse_r(self, context):
        """
        Parse the running text.
        """
        if not context.parsed_result:
            return ''

        applicable_styles = self.parse_r_determine_applicable_styles(context)

        # Apply all the handlers.
        parsed_result = context.parsed_result
        for func in applicable_styles:
            parsed_result = func(parsed_result)

        return parsed_result

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
    def heading(self, text, heading_style_name):
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
