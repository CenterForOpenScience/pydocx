# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.openxml.packaging import MainDocumentPart
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import PyDocXHTMLExporterNoStyle, WordprocessingDocumentFactory


class ExporterThatReturnsNoneForHead(PyDocXHTMLExporterNoStyle):
    def head(self):
        pass


class ExporterThatReturnsNoneForHeadTestCase(DocumentGeneratorTestCase):
    exporter = ExporterThatReturnsNoneForHead

    def format_expected_html(self, html):
        return html

    def test_empty_head(self):
        document_xml = '<p><r><t>Foo</t></r></p>'

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<html><body><p>Foo</p></body></html>'
        self.assert_document_generates_html(document, expected_html)
