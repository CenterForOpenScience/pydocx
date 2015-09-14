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
    def test_one_row_one_cell_one_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r>
                                <t>Foo</t>
                            </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_multiple_paragraphs(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r>
                                <t>Foo</t>
                            </r>
                        </p>
                        <p>
                            <r>
                                <t>Bar</t>
                            </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo<br />Bar</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_two_rows_two_cells_one_paragraph_each(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r>
                                <t>Foo</t>
                            </r>
                        </p>
                    </tc>
                    <tc>
                        <p>
                            <r>
                                <t>Bar</t>
                            </r>
                        </p>
                    </tc>
                </tr>
                <tr>
                    <tc>
                        <p>
                            <r>
                                <t>One</t>
                            </r>
                        </p>
                    </tc>
                    <tc>
                        <p>
                            <r>
                                <t>Two</t>
                            </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                    <td>Bar</td>
                </tr>
                <tr>
                    <td>One</td>
                    <td>Two</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_empty(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td></td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_cell_with_character_styles_applied(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r>
                                <rPr>
                                    <b />
                                    <i />
                                </rPr>
                                <t>Foo</t>
                            </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td><em><strong>Foo</strong></em></td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_two_rows_two_cells_with_colspan(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <tcPr>
                            <gridSpan val="2" />
                        </tcPr>
                        <p>
                            <r>
                                <t>Foo</t>
                            </r>
                        </p>
                    </tc>
                </tr>
                <tr>
                    <tc>
                        <p>
                            <r>
                                <t>One</t>
                            </r>
                        </p>
                    </tc>
                    <tc>
                        <p>
                            <r>
                                <t>Two</t>
                            </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td colspan="2">Foo</td>
                </tr>
                <tr>
                    <td>One</td>
                    <td>Two</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_two_rows_two_cells_with_rowspan(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <tcPr>
                            <vMerge val="restart" />
                        </tcPr>
                        <p>
                            <r>
                                <t>Foo</t>
                            </r>
                        </p>
                    </tc>
                    <tc>
                        <p>
                            <r>
                                <t>Bar</t>
                            </r>
                        </p>
                    </tc>
                </tr>
                <tr>
                    <tc>
                        <tcPr>
                            <vMerge val="continue" />
                        </tcPr>
                    </tc>
                    <tc>
                        <p>
                            <r>
                                <t>Two</t>
                            </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td rowspan="2">Foo</td>
                    <td>Bar</td>
                </tr>
                <tr>
                    <td>Two</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_empty_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td></td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_empty_paragraph_after_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                        <p>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_empty_paragraph_before_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                        </p>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_paragraph_that_has_empty_run_before_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r></r>
                        </p>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_paragraph_that_has_empty_run_after_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                        <p>
                            <r></r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_empty_text_before_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r><t></t></r>
                        </p>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_empty_text_after_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                        <p>
                            <r><t></t></r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_row_one_cell_with_whitespace_after_other_paragraph(self):
        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                            <r><t>Foo</t></r>
                        </p>
                        <p>
                            <r><t> </t></r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td>Foo</td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)
