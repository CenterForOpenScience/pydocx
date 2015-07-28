# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging import MainDocumentPart
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class HyperlinkTestCase(DocumentGeneratorTestCase):
    def test_single_run(self):
        document_xml = '''
            <p>
              <hyperlink id="foobar">
                <r>
                  <t>link</t>
                </r>
              </hyperlink>
              <r>
                <t>.</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type='foo/hyperlink',
            target='http://google.com',
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '<p><a href="http://google.com">link</a>.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_multiple_runs(self):
        document_xml = '''
            <p>
              <hyperlink id="foobar">
                <r>
                  <t>l</t>
                  <t>i</t>
                  <t>n</t>
                  <t>k</t>
                </r>
              </hyperlink>
              <r>
                <t>.</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type='foo/hyperlink',
            target='http://google.com',
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '<p><a href="http://google.com">link</a>.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_link_text(self):
        document_xml = '''
            <p>
              <hyperlink id="foobar" />
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type='foo/hyperlink',
            target='http://google.com',
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = ''
        self.assert_document_generates_html(document, expected_html)

    def test_undefined_relationship(self):
        document_xml = '''
            <p>
              <hyperlink id="foobar">
                <r>
                  <t>link</t>
                </r>
              </hyperlink>
              <r>
                <t>.</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>link.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_with_line_break(self):
        document_xml = '''
            <p>
              <hyperlink id="foobar">
                <r>
                  <t>li</t>
                  <br />
                  <t>nk</t>
                </r>
              </hyperlink>
              <r>
                <t>.</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type='foo/hyperlink',
            target='http://google.com',
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '<p><a href="http://google.com">li<br />nk</a>.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_underline_style_ignored(self):
        document_xml = '''
            <p>
              <hyperlink id="foobar">
                <r>
                  <rPr>
                    <u val="single" />
                  </rPr>
                  <t>link</t>
                </r>
              </hyperlink>
              <r>
                <t>.</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document_rels = document.relationship_format.format(
            id='foobar',
            type='foo/hyperlink',
            target='http://google.com',
            target_mode='External',
        )

        document.add(MainDocumentPart, document_xml, document_rels)

        expected_html = '<p><a href="http://google.com">link</a>.</p>'
        self.assert_document_generates_html(document, expected_html)
