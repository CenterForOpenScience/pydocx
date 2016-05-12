# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart


class TableTestCase(DocumentGeneratorTestCase):
    def test_textbox_with_content(self):
        document_xml = '''
            <p>
                <r>
                    <AlternateContent>
                        <Fallback>
                            <pict>
                                <shape>
                                    <textbox>
                                        <txbxContent>
                                            <p>
                                                <r>
                                                    <t>AAA</t>
                                                </r>
                                            </p>
                                        </txbxContent>
                                    </textbox>
                                </shape>
                            </pict>
                        </Fallback>
                    </AlternateContent>
                </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                <p>
                    AAA
                </p>
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_textbox_with_content_outside_of_textbox(self):
        document_xml = '''
            <p>
                <r><t>AAA</t></r>
                <r>
                    <AlternateContent>
                        <Fallback>
                            <pict>
                                <shape>
                                    <textbox>
                                        <txbxContent>
                                            <p>
                                                <r>
                                                    <t>BBB</t>
                                                </r>
                                            </p>
                                        </txbxContent>
                                    </textbox>
                                </shape>
                            </pict>
                        </Fallback>
                    </AlternateContent>
                </r>
                <r><t>CCC</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                AAA
                <p>
                    BBB
                </p>
                CCC
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)
