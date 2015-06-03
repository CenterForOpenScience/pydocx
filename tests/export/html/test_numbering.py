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
    simple_list_item = '''
        <p>
            <pPr>
                <numPr>
                    <ilvl val="{ilvl}" />
                    <numId val="{num_id}" />
                </numPr>
            </pPr>
            <r><t>{content}</t></r>
        </p>
    '''

    simple_list_definition = '''
        <num numId="{num_id}">
            <abstractNumId val="{num_id}"/>
        </num>
        <abstractNum abstractNumId="{num_id}">
            <lvl ilvl="0">
                <numFmt val="{num_format}"/>
            </lvl>
        </abstractNum>
    '''

    def test_lowerLetter_numbering_format_is_handled(self):
        num_id = 1
        numbering_xml = self.simple_list_definition.format(
            num_id=num_id,
            num_format='lowerLetter',
        )

        document_xml = self.simple_list_item.format(
            content='AAA',
            num_id=num_id,
            ilvl=0,
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_single_level_list_with_surrounding_paragraphs(self):
        num_id = 1
        numbering_xml = self.simple_list_definition.format(
            num_id=num_id,
            num_format='lowerLetter',
        )

        document_xml = '''
            <p><r><t>Foo</t></r></p>
            {aaa}
            {bbb}
            <p><r><t>Bar</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=num_id,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=num_id,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>Foo</p>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
                <li>BBB</li>
            </ol>
            <p>Bar</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_multi_level_list_with_surrounding_paragraphs(self):
        num_id = 1
        numbering_xml = '''
            <num numId="{num_id}">
                <abstractNumId val="{num_id}"/>
            </num>
            <abstractNum abstractNumId="{num_id}">
                <lvl ilvl="0">
                    <numFmt val="lowerLetter"/>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="decimal"/>
                </lvl>
                <lvl ilvl="2">
                    <numFmt val="upperLetter"/>
                </lvl>
            </abstractNum>
        '''.format(num_id=num_id)

        document_xml = '''
            <p><r><t>Foo</t></r></p>
            {aaa}
            {bbb}
            {ccc}
            <p><r><t>Bar</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=num_id,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=num_id,
                ilvl=1,
            ),
            ccc=self.simple_list_item.format(
                content='CCC',
                num_id=num_id,
                ilvl=2,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>Foo</p>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA
                    <ol class="pydocx-list-style-type-decimal">
                        <li>BBB
                            <ol class="pydocx-list-style-type-upperLetter">
                                <li>CCC</li>
                            </ol>
                        </li>
                    </ol>
                </li>
            </ol>
            <p>Bar</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_adjacent_lists(self):
        numbering_xml = '''
            {letter}
            {decimal}
        '''.format(
            letter=self.simple_list_definition.format(
                num_id=1,
                num_format='lowerLetter',
            ),
            decimal=self.simple_list_definition.format(
                num_id=2,
                num_format='decimal',
            ),
        )

        document_xml = '''
            <p><r><t>Foo</t></r></p>
            {aaa}
            {bbb}
            <p><r><t>Bar</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=2,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>Foo</p>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
            </ol>
            <ol class="pydocx-list-style-type-decimal">
                <li>BBB</li>
            </ol>
            <p>Bar</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_separate_lists_with_paragraph_in_between_and_after(self):
        numbering_xml = '''
            {letter}
            {decimal}
        '''.format(
            letter=self.simple_list_definition.format(
                num_id=1,
                num_format='lowerLetter',
            ),
            decimal=self.simple_list_definition.format(
                num_id=2,
                num_format='decimal',
            ),
        )

        document_xml = '''
            <p><r><t>Foo</t></r></p>
            {aaa}
            <p><r><t>Bar</t></r></p>
            {bbb}
            <p><r><t>Baz</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=2,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>Foo</p>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
            </ol>
            <p>Bar</p>
            <ol class="pydocx-list-style-type-decimal">
                <li>BBB</li>
            </ol>
            <p>Baz</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_single_list_followed_by_paragraph(self):
        numbering_xml = '''
            {letter}
        '''.format(
            letter=self.simple_list_definition.format(
                num_id=1,
                num_format='lowerLetter',
            ),
        )

        document_xml = '''
            {aaa}
            <p><r><t>Foo</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
            </ol>
            <p>Foo</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_single_list_with_bare_paragraph_between_items(self):
        numbering_xml = '''
            {letter}
        '''.format(
            letter=self.simple_list_definition.format(
                num_id=1,
                num_format='lowerLetter',
            ),
        )

        document_xml = '''
            {aaa}
            <p><r><t>Foo</t></r></p>
            {bbb}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA<br />Foo</li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_list_with_empty_numbering_xml(self):
        numbering_xml = ''

        document_xml = '''
            {aaa}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-None">
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)
