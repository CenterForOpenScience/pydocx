# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import xml.sax.saxutils

from pydocx.constants import TWIPS_PER_POINT
from pydocx.exceptions import MalformedDocxException
from pydocx.export.numbering_span import (
    NumberingItem,
    NumberingSpan,
    NumberingSpanBuilder,
)
from pydocx.openxml import wordprocessing, vml
from pydocx.openxml.packaging import WordprocessingDocument


class PyDocXExporter(object):
    def __init__(self, path):
        self.path = path
        self._document = None
        self._page_width = None
        self.previous = {}

        self.footnote_tracker = []

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
            wordprocessing.Picture: self.export_picture,
            wordprocessing.DeletedRun: self.export_deleted_run,
            wordprocessing.DeletedText: self.export_deleted_text,
            wordprocessing.FootnoteReference: self.export_footnote_reference,
            wordprocessing.Footnote: self.export_footnote,
            wordprocessing.FootnoteReferenceMark: self.export_footnote_reference_mark,
            wordprocessing.SdtRun: self.export_sdt_run,
            wordprocessing.SdtContentRun: self.export_sdt_content_run,
            wordprocessing.SdtBlock: self.export_sdt_block,
            wordprocessing.SdtContentBlock: self.export_sdt_content_block,
            wordprocessing.TabChar: self.export_tab_char,
            vml.Shape: self.export_vml_shape,
            vml.ImageData: self.export_vml_image_data,
            NumberingSpan: self.export_numbering_span,
            NumberingItem: self.export_numbering_item,
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

    def export(self):
        if self.main_document_part is None:
            raise MalformedDocxException
        document = self.main_document_part.document
        if document:
            for result in self.export_node(document):
                yield result

    def export_node(self, node):
        caller = self.node_type_to_export_func_map.get(type(node))
        if callable(caller):
            for result in caller(node):
                yield result

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

    def yield_numbering_spans(self, items):
        builder = NumberingSpanBuilder(items)
        numbering_spans = builder.get_numbering_spans()
        for item in numbering_spans:
            yield item

    def export_body(self, body):
        numbering_spans = self.yield_numbering_spans(body.children)
        return self.yield_nested(numbering_spans, self.export_node)

    def export_paragraph(self, paragraph):
        results = self.yield_nested(paragraph.children, self.export_node)
        if paragraph.effective_properties:
            results = self.export_paragraph_apply_properties(paragraph, results)
        return results

    def get_paragraph_styles_to_apply(self, paragraph):
        properties = paragraph.effective_properties
        property_rules = [
            (properties.justification, self.export_paragraph_property_justification),
            (properties.indentation, self.export_paragraph_property_indentation),
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
        return
        yield

    def export_run(self, run):
        # TODO squash multiple sequential text nodes into one?
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
            (properties.vertical_align, self.export_run_property_vertical_align),
        ]
        for actual_value, handler in property_rules:
            if actual_value:
                yield handler

    def export_run_apply_properties(self, run, results):
        styles_to_apply = self.get_run_styles_to_apply(run)
        # Preserve style application order, but don't duplicate
        applied_styles = set()
        for func in styles_to_apply:
            if func not in applied_styles:
                results = func(run, results)
                applied_styles.add(func)
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
            # TODO should we do this here, or in the HTML exporter?
            yield self.escape(text.text)

    def export_deleted_text(self, deleted_text):
        return
        yield

    def export_no_break_hyphen(self, hyphen):
        yield '-'

    def export_table(self, table):
        return self.yield_nested(table.rows, self.export_node)

    def export_table_row(self, table_row):
        return self.yield_nested(table_row.cells, self.export_node)

    def export_table_cell(self, table_cell):
        numbering_spans = self.yield_numbering_spans(table_cell.children)
        return self.yield_nested(numbering_spans, self.export_node)

    def escape(self, text):
        #  TODO should we use escape here instead?
        return xml.sax.saxutils.quoteattr(text)[1:-1]

    def export_drawing(self, drawing):
        return
        yield

    def export_smart_tag_run(self, smart_tag):
        return self.yield_nested(smart_tag.children, self.export_node)

    def export_inserted_run(self, inserted_run):
        return self.yield_nested(inserted_run.children, self.export_node)

    def export_picture(self, picture):
        return self.yield_nested(picture.children, self.export_node)

    def export_deleted_run(self, deleted_run):
        return self.yield_nested(deleted_run.children, self.export_node)

    def export_footnote_reference(self, footnote_reference):
        if footnote_reference.footnote is None:
            return
        self.footnote_tracker.append(footnote_reference)
        footnote_index = len(self.footnote_tracker)
        yield '{0}'.format(footnote_index)

    def export_footnote(self, footnote):
        # TODO a footnote can have paragraph children, should we track
        # numbering?
        return self.yield_nested(footnote.children, self.export_node)

    def export_footnotes(self):
        if not self.footnote_tracker:
            return
        for footnote_reference in self.footnote_tracker:
            footnote = footnote_reference.footnote
            if footnote:
                for result in self.export_node(footnote):
                    yield result

    def export_footnote_reference_mark(self, footnote_reference_mark):
        return
        yield

    def export_vml_shape(self, shape):
        return self.yield_nested(shape.children, self.export_node)

    def export_vml_image_data(self, image_data):
        return
        yield

    def export_sdt(self, sdt):
        return self.export_node(sdt.content)

    def export_sdt_content(self, sdt_content):
        return self.yield_nested(sdt_content.children, self.export_node)

    def export_sdt_run(self, sdt_run):
        return self.export_sdt(sdt_run)

    def export_sdt_content_run(self, sdt_content_run):
        return self.export_sdt_content(sdt_content_run)

    def export_sdt_block(self, sdt_block):
        return self.export_sdt(sdt_block)

    def export_sdt_content_block(self, sdt_content_block):
        return self.export_sdt_content(sdt_content_block)

    def export_tab_char(self, tab_char):
        return
        yield

    def export_numbering_span(self, numbering_span):
        return self.yield_nested(numbering_span.children, self.export_node)

    def export_numbering_item(self, numbering_item):
        return self.yield_nested(numbering_item.children, self.export_node)
