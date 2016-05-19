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
                    <t>BBB</t>
                    <AlternateContent>
                        <Fallback>
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
                        </Fallback>
                    </AlternateContent>
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

    def test_fallback_is_only_text(self):
        document_xml = '''
            <p>
                <r><t>AAA</t></r>
                <r>
                    <t>BBB</t>
                    <AlternateContent>
                        <Fallback>
                            <t>CCC</t>
                        </Fallback>
                    </AlternateContent>
                    <t>DDD</t>
                </r>
                <r><t>EEE</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAABBBCCCDDDEEE</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_fallback_contains_a_table(self):
        document_xml = '''
            <p>
                <r><t>AAA</t></r>
                <r>
                    <t>BBB</t>
                </r>
            </p>
            <AlternateContent>
                <Fallback>
                    <tbl>
                        <tr>
                            <tc>
                                <p>
                                    <r>
                                        <t>CCC</t>
                                    </r>
                                </p>
                            </tc>
                        </tr>
                    </tbl>
                </Fallback>
            </AlternateContent>
            <p>
                <r>
                    <t>DDD</t>
                </r>
                <r><t>EEE</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAABBB</p>
            <table border="1">
                <tr>
                    <td>CCC</td>
                </tr>
            </table>
            <p>DDDEEE</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_fallback_has_invalid_children(self):
        # Currently, we are cheating when we define the valid children of a
        # Fallback element. Right now we are saying that all children are
        # valid. This is not technically true. In the loosest of senses, yes
        # the Fallback can include any child element. However, the valid
        # children for Fallback need to be inherited by it's grand parents.
        # This test is showing an invalid child for Fallback. When #215 gets
        # fixed, this test should fail. When it does, you'll want to strip out
        # the table from the expected_html.
        document_xml = '''
            <p>
                <r><t>AAA</t></r>
                <r>
                    <t>BBB</t>
                    <AlternateContent>
                        <Fallback>
                            <tbl>
                                <tr>
                                    <tc>
                                        <p>
                                            <r>
                                                <t>CCC</t>
                                            </r>
                                        </p>
                                    </tc>
                                </tr>
                            </tbl>
                        </Fallback>
                    </AlternateContent>
                    <t>DDD</t>
                </r>
                <r><t>EEE</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAABBB
                <table border="1">
                    <tr>
                        <td>CCC</td>
                    </tr>
                </table>
            DDDEEE</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_fallback_is_in_root(self):
        document_xml = '''
        <AlternateContent>
            <Fallback>
                <p>
                    <r>
                        <t>AAA</t>
                    </r>
                </p>
            </Fallback>
        </AlternateContent>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAA</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_choice_is_ignored(self):
        document_xml = '''
        <AlternateContent>
            <Choice>
                <p>
                    <r>
                        <t>Ignored</t>
                    </r>
                </p>
            </Choice>
            <Fallback>
                <p>
                    <r>
                        <t>AAA</t>
                    </r>
                </p>
            </Fallback>
        </AlternateContent>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAA</p>
        '''
        self.assert_document_generates_html(document, expected_html)
