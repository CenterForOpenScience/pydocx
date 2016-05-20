# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart


class RectTestCase(DocumentGeneratorTestCase):
    def test_rect_with_textbox(self):
        document_xml = '''
            <p>
                <r>
                    <pict>
                        <rect>
                            <textbox>
                                <txbxContent>
                                    <p>
                                        <r>
                                            <t>AAA</t>
                                        </r>
                                    </p>
                                </txbxContent>
                            </textbox>
                        </rect>
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
