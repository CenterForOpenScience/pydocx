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
                    <t>BBB</t>
                    <pict>
                        <shape>
                            <textbox>
                                <txbxContent>
                                    <p>
                                        <r>
                                            <t>CCC</t>
                                        </r>
                                    </p>
                                </txbxContent>
                            </textbox>
                        </shape>
                    </pict>
                    <t>DDD</t>
                </r>
                <r><t>EEE</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                AAABBB
                <p>
                    CCC
                </p>
                DDDEEE
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_textbox_with_a_table(self):
        document_xml = '''
            <p>
                <r>
                    <pict>
                        <shape>
                            <textbox>
                                <txbxContent>
                                    <tbl>
                                        <tr>
                                            <tc>
                                                <p>
                                                    <r>
                                                        <t>AAA</t>
                                                    </r>
                                                </p>
                                            </tc>
                                        </tr>
                                    </tbl>
                                </txbxContent>
                            </textbox>
                        </shape>
                    </pict>
                </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>AAA</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_textbox_with_a_table_and_other_runs(self):
        document_xml = '''
            <p>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <pict>
                        <shape>
                            <textbox>
                                <txbxContent>
                                    <tbl>
                                        <tr>
                                            <tc>
                                                <p>
                                                    <r>
                                                        <t>BBB</t>
                                                    </r>
                                                </p>
                                            </tc>
                                        </tr>
                                    </tbl>
                                </txbxContent>
                            </textbox>
                        </shape>
                    </pict>
                </r>
                <r>
                    <t>CCC</t>
                </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        # TODO This should probably put AAA and CCC in their own paragraphs so
        # the root would be `p table p` but we can deal with that later.
        expected_html = '''
            <p>
                AAA
                <table border="1">
                    <tr>
                        <td>BBB</td>
                    </tr>
                </table>
                CCC
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)
