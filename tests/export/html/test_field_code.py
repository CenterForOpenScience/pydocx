# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.openxml.packaging import MainDocumentPart
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class FieldCodeTestCase(DocumentGeneratorTestCase):
    def test_hyperlink_within_single_paragraph(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "https://www.google.com/"</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Link: <a href="http://www.google.com">AAA</a></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_hyperlink_spanning_multiple_paragraphs(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
            </p>
            <p>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "https://www.google.com/"</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <t>BBB</t>
                </r>
            </p>
            <p><r><t>CCC</t></r></p>
            <p>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>Link: </p>
            <p><a href="http://www.google.com">AAABBB</a></p>
            <p><a href="http://www.google.com">CCC</a>.</p>
        '''
        self.assert_document_generates_html(document, expected_html)
