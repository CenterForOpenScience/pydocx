# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart


class DirectFormattingBoldPropertyTestCase(DocumentGeneratorTestCase):
    def test_default_no_val_set(self):
        document_xml = '''
            <p>
              <r>
                <rPr>
                  <b />
                </rPr>
                <t>foo</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><strong>foo</strong></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_valid_enable_vals_create_strong(self):
        vals = [
            'true',
            'on',
            '1',
            '',
        ]
        paragraph_template = '''
            <p>
              <r>
                <rPr>
                  <b val="%s" />
                </rPr>
                <t>foo</t>
              </r>
            </p>
        '''
        document_xml = ''.join(
            paragraph_template % val
            for val in vals
        )

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p><strong>foo</strong></p>
            <p><strong>foo</strong></p>
            <p><strong>foo</strong></p>
            <p><strong>foo</strong></p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_valid_disabled_vals_do_not_create_strong(self):
        vals = [
            'off',
            'false',
            'none',
            '0',
        ]
        paragraph_template = '''
            <p>
              <r>
                <rPr>
                  <b val="%s" />
                </rPr>
                <t>foo</t>
              </r>
            </p>
        '''
        document_xml = ''.join(
            paragraph_template % val
            for val in vals
        )

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>foo</p>
            <p>foo</p>
            <p>foo</p>
            <p>foo</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_invalid_vals_do_not_create_strong(self):
        vals = [
            'foo',
            'bar',
        ]
        paragraph_template = '''
            <p>
              <r>
                <rPr>
                  <b val="%s" />
                </rPr>
                <t>foo</t>
              </r>
            </p>
        '''
        document_xml = ''.join(
            paragraph_template % val
            for val in vals
        )

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>foo</p>
            <p>foo</p>
        '''
        self.assert_document_generates_html(document, expected_html)
