# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.openxml.packaging import MainDocumentPart
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class HyperlinkSimpleFieldTestCase(DocumentGeneratorTestCase):
    def test_single_run(self):
        document_xml = '''
            <p>
                <fldSimple instr="HYPERLINK http://www.google.com">
                    <r>
                        <rPr>
                            <b />
                        </rPr>
                        <t>AAA</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                <a href="http://www.google.com">
                    <strong>AAA</strong>
                </a>
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_multiple_runs(self):
        document_xml = '''
            <p>
                <fldSimple instr="HYPERLINK http://www.google.com">
                    <r>
                        <rPr>
                            <b />
                        </rPr>
                        <t>AAA</t>
                    </r>
                    <r>
                        <rPr>
                            <i />
                        </rPr>
                        <t>BBB</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                <a href="http://www.google.com">
                    <strong>AAA</strong>
                    <em>BBB</em>
                </a>
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)
