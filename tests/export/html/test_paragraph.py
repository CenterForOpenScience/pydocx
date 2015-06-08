# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart


class ParagraphTestCase(DocumentGeneratorTestCase):
    def test_multiple_text_tags_in_a_single_run_tag_create_single_paragraph(
        self,
    ):
        document_xml = '''
            <p>
              <r>
                <t>A</t>
                <t>B</t>
                <t>C</t>
              </r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>ABC</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_empty_text_tag_does_not_create_paragraph(self):
        document_xml = '''
            <p>
              <r>
                <t></t>
              </r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = ''
        self.assert_document_generates_html(document, expected_html)

    def test_unicode_character_from_xml_entity(self):
        document_xml = '''
            <p>
              <r>
                <t>&#x10001F;</t>
              </r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>\U0010001f</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_non_entity_unicode_character(self):
        document_xml = '''
            <p>
              <r>
                <t>capacités</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>capacités</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_tab_char_with_text(self):
        document_xml = '''
            <p>
              <r>
                <t>foo</t>
                <tab />
                <t>bar</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>foo<span class="pydocx-tab"></span>bar</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_tab_char_by_itself(self):
        document_xml = '''
            <p>
              <r>
                <tab />
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><span class="pydocx-tab"></span></p>'
        self.assert_document_generates_html(document, expected_html)
