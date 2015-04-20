# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart, NumberingDefinitionsPart


class NumberingTestCase(DocumentGeneratorTestCase):
    def test_lowerLetter_numbering_format_is_handled(self):
        num_id = '2'
        numbering_xml = '''
            <num numId="{num_id}">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="lowerLetter"/>
                </lvl>
            </abstractNum>
        '''.format(num_id=num_id)

        document_xml = '''
            <p>
                <pPr>
                    <numPr>
                        <ilvl val="0" />
                        <numId val="{num_id}" />
                    </numPr>
                </pPr>
                <r><t>AAA</t></r>
            </p>
        '''.format(num_id=num_id)

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)
