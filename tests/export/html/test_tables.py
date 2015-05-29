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
    def test_simple_table(self):
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
