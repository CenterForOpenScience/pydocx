# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export.numbering_span import BaseNumberingSpanBuilder
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import (
    PyDocXHTMLExporterNoStyle,
    WordprocessingDocumentFactory,
)
from pydocx.openxml.packaging import (
    MainDocumentPart,
    NumberingDefinitionsPart,
    StyleDefinitionsPart,
)
from pydocx.export.numbering_span import int_to_alpha, int_to_roman


class NumberingTestBase(object):
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


class NumberingTestCase(NumberingTestBase, DocumentGeneratorTestCase):
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

    def test_basic_list_followed_by_list_that_is_heading_and_paragraph(self):
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

        style_xml = '''
            <style styleId="style1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        list_item_with_parent_style_heading = '''
            <p>
                <pPr>
                    <pStyle val="style1" />
                    <numPr>
                        <ilvl val="{ilvl}" />
                        <numId val="{num_id}" />
                    </numPr>
                </pPr>
                <r><t>{content}</t></r>
            </p>
        '''

        document_xml = '''
            {aaa}
            {bbb}
            <p><r><t>Bar</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=list_item_with_parent_style_heading.format(
                content='BBB',
                num_id=2,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA</li>
            </ol>
            <ol class="pydocx-list-style-type-decimal">
                <li>
                    <strong>BBB</strong>
                </li>
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
            <p>AAA</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_single_paragraph_missing_level_definition(self):
        numbering_xml = '''
            {letter}
        '''.format(
            letter=self.simple_list_definition.format(
                num_id=1,
                num_format='lowerLetter',
            ),
        )

        document_xml = '''
            <p>
                <pPr>
                    <numPr>
                        <numId val="1" />
                    </numPr>
                </pPr>
                <r><t>foo</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>foo</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_multiple_paragraphs_with_one_missing_level_definition(self):
        numbering_xml = '''
            {letter}
        '''.format(
            letter=self.simple_list_definition.format(
                num_id=1,
                num_format='lowerLetter',
            ),
        )

        document_xml = '''
            <p><r><t>foo</t></r></p>
            <p>
                <pPr>
                    <numPr>
                        <numId val="1" />
                    </numPr>
                </pPr>
                <r><t>bar</t></r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>foo</p>
            <p>bar</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_with_valid_list_level_followed_by_missing_level(self):
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
            <p>
                <pPr>
                    <numPr>
                        <numId val="1" />
                    </numPr>
                </pPr>
                <r><t>foo</t></r>
            </p>
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
            <p>foo</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_missing_level_in_between_valid_levels(self):
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
            <p>
                <pPr>
                    <numPr>
                        <numId val="1" />
                    </numPr>
                </pPr>
                <r><t>foo</t></r>
            </p>
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
                <li>
                    AAA
                    <br />
                    foo
                </li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_empty_paragraph_after_list_item(self):
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
            <p />
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
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_empty_paragraph_in_between_list_items(self):
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
            <p />
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
                <li>AAA</li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_and_run_with_empty_text_in_between_list_items(self):
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
            <p>
                <r><t></t></r>
            </p>
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
                <li>AAA</li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_with_empty_run_in_between_list_items(self):
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
            <p>
                <r></r>
            </p>
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
                <li>AAA</li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_with_empty_run_followed_by_non_empty_paragraph(self):
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
            <p>
                <r></r>
            </p>
            <p>
                <r><t>BBB</t></r>
            </p>
            {ccc}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            ccc=self.simple_list_item.format(
                content='CCC',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA<br />BBB</li>
                <li>CCC</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_with_multiple_empty_runs_followed_by_non_empty_paragraph(self):
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
            <p>
                <r></r>
            </p>
            <p>
                <r></r>
            </p>
            <p>
                <r></r>
            </p>
            <p>
                <r><t>BBB</t></r>
            </p>
            {ccc}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            ccc=self.simple_list_item.format(
                content='CCC',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA<br />BBB</li>
                <li>CCC</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_empty_run_paragraph_empty_run_paragraph(self):
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
            <p>
                <r></r>
            </p>
            <p>
                <r><t>Foo</t></r>
            </p>
            <p>
                <r></r>
            </p>
            <p>
                <r><t>Bar</t></r>
            </p>
            {ccc}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            ccc=self.simple_list_item.format(
                content='CCC',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>AAA<br />Foo<br />Bar</li>
                <li>CCC</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_followed_by_paragraph_with_only_whitespace(self):
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
            <p>
                <r><t> </t></r>
            </p>
            {ccc}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            ccc=self.simple_list_item.format(
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
                <li>AAA</li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_empty_item(self):
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
        '''.format(
            aaa=self.simple_list_item.format(
                content='',
                num_id=1,
                ilvl=0,
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-lowerLetter">
                <li></li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_numfmt_None_causes_list_to_be_ignored(self):
        document_xml = '''
            {aaa}
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

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="none"/>
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAA</p>
            <p>BBB</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_numfmt_None_causes_sub_list_to_be_ignored(self):
        document_xml = '''
            {aaa}
            {bbb}
            {ccc}
            {ddd}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=1,
                ilvl=1,
            ),
            ccc=self.simple_list_item.format(
                content='CCC',
                num_id=1,
                ilvl=1,
            ),
            ddd=self.simple_list_item.format(
                content='DDD',
                num_id=1,
                ilvl=0,
            ),
        )

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="none"/>
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>
                    AAA
                    <br />
                    BBB
                    <br />
                    CCC
                </li>
                <li>DDD</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_root_level_numfmt_None_with_sublist(self):
        document_xml = '''
            {aaa}
            {bbb}
            {ccc}
            {ddd}
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=1,
                ilvl=1,
            ),
            ccc=self.simple_list_item.format(
                content='CCC',
                num_id=1,
                ilvl=1,
            ),
            ddd=self.simple_list_item.format(
                content='DDD',
                num_id=1,
                ilvl=0,
            ),
        )

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="none"/>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>AAA</p>
            <ol class="pydocx-list-style-type-decimal">
                <li>BBB</li>
                <li>CCC</li>
            </ol>
            <p>DDD</p>
        '''
        self.assert_document_generates_html(document, expected_html)


class FakedNumberingManyItemsTestCase(NumberingTestBase, DocumentGeneratorTestCase):
    def assert_html(self, list_type, digit_generator):
        paragraphs = []
        expected_items = []
        for i in range(1, 100):
            content = 'Foo-{i}'.format(i=i)
            digit = digit_generator(i)
            paragraphs.append(
                '<p><r><t>{digit}. {content}</t></r></p>'.format(
                    digit=digit,
                    content=content,
                ),
            )
            expected_items.append(content)

        document_xml = ''.join(paragraphs)

        items = [
            '<li>{item}</li>'.format(item=item)
            for item in expected_items
        ]

        expected_html = '''
            <ol class="pydocx-list-style-type-{list_type}">
            {items}
            </ol>
        '''.format(
            list_type=list_type,
            items=''.join(items),
        )

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_fake_decimal_list_with_many_items(self):
        self.assert_html('decimal', int)

    def test_fake_lower_alpha_list_with_many_items(self):
        def digit_generator(index):
            return int_to_alpha(index).lower()

        self.assert_html('lowerLetter', digit_generator)

    def test_fake_upper_alpha_list_with_many_items(self):
        def digit_generator(index):
            return int_to_alpha(index).upper()

        self.assert_html('upperLetter', digit_generator)

    def test_fake_upper_roman_list_with_many_items(self):
        def digit_generator(index):
            return int_to_roman(index).upper()

        self.assert_html('upperRoman', digit_generator)

    def test_fake_lower_roman_list_with_many_items(self):
        def digit_generator(index):
            return int_to_roman(index).lower()

        self.assert_html('lowerRoman', digit_generator)


class FakedNumberingTestCase(NumberingTestBase, DocumentGeneratorTestCase):
    def test_real_list_plus_fake_list(self):
        document_xml = '''
            {foo}
            <p><r><t>2. Bar</t></r></p>
            <p><r><t>3. Baz</t></r></p>
        '''.format(
            foo=self.simple_list_item.format(
                content='Foo',
                num_id=1,
                ilvl=0,
            ),
        )

        # This works because simple_list_definition doesn't define an
        # indentation for the level. So the real list indentation is
        # effectively 0
        numbering_xml = '''
            {decimal}
        '''.format(
            decimal=self.simple_list_definition.format(
                num_id=1,
                num_format='decimal',
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>Foo</li>
                <li>Bar</li>
                <li>Baz</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_real_list_plus_tab_nested_fake_list_with_mixed_formats(self):
        document_xml = '''
            {aaa}
            <p><r><tab /><t>a. BBB</t></r></p>
            <p><r><tab /><t>b. CCC</t></r></p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
        )

        # This works because simple_list_definition doesn't define an
        # indentation for the level. So the real list indentation is
        # effectively 0
        numbering_xml = '''
            {decimal}
        '''.format(
            decimal=self.simple_list_definition.format(
                num_id=1,
                num_format='decimal',
            ),
        )

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AAA
                    <ol class="pydocx-list-style-type-lowerLetter">
                        <li>BBB</li>
                        <li>CCC</li>
                    </ol>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_initial_faked_list_plus_real_list(self):
        document_xml = '''
            <p><r><t>1. Foo</t></r></p>
            <p><r><t>2. Bar</t></r></p>
            {foo}
        '''.format(
            foo=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
        )

        # This works because the level definition doesn't define an indentation
        # for the level. So the real list indentation is effectively 0
        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                    <start val="3" />
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>Foo</li>
                <li>Bar</li>
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_one_fake_list_followed_by_another_fake_list_same_format(self):
        document_xml = '''
            <p><r><t>1. AA</t></r></p>
            <p><r><t>2. AB</t></r></p>
            <p><r><t>1. BA</t></r></p>
            <p><r><t>2. BB</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AA</li>
                <li>AB</li>
            </ol>
            <ol class="pydocx-list-style-type-decimal">
                <li>BA</li>
                <li>BB</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_one_fake_list_followed_by_another_fake_list_different_format(self):
        document_xml = '''
            <p><r><t>1. AA</t></r></p>
            <p><r><t>2. AB</t></r></p>
            <p><r><t>a. BA</t></r></p>
            <p><r><t>b. BB</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AA</li>
                <li>AB</li>
            </ol>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>BA</li>
                <li>BB</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_real_nested_list_continuation_fake_nested_list_using_indentation(self):
        document_xml = '''
            {aaa}
            {bbb}
            <p>
                <pPr>
                    <ind left="720" hanging="0" />
                </pPr>
                <r><t>2. CCC</t></r>
            </p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=1,
                ilvl=1,
            ),
        )

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                    <pPr>
                        <ind left="720" hanging="360" />
                    </pPr>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="decimal" />
                    <pPr>
                        <ind left="720" hanging="0" />
                    </pPr>
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AAA
                    <ol class="pydocx-list-style-type-decimal">
                        <li>BBB</li>
                        <li>CCC</li>
                    </ol>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_real_nested_list_continuation_fake_list_using_indentation(self):
        document_xml = '''
            {aaa}
            {bbb}
            <p>
                <pPr>
                    <ind left="720" hanging="360" />
                </pPr>
                <r><t>2. CCC</t></r>
            </p>
        '''.format(
            aaa=self.simple_list_item.format(
                content='AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='BBB',
                num_id=1,
                ilvl=1,
            ),
        )

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                    <pPr>
                        <ind left="720" hanging="360" />
                    </pPr>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="decimal" />
                    <pPr>
                        <ind left="720" hanging="0" />
                    </pPr>
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AAA
                    <ol class="pydocx-list-style-type-decimal">
                        <li>BBB</li>
                    </ol>
                </li>
                <li>CCC</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_faked_list_using_indentation(self):
        document_xml = '''
            <p><r><t>1. AA</t></r></p>
            <p>
                <pPr>
                    <ind left="200" />
                </pPr>
                <r><t>a. AAA</t></r>
            </p>
            <p>
                <pPr>
                    <ind left="0" firstLine="200" />
                </pPr>
                <r><t>b. AAB</t></r>
            </p>
            <p>
                <pPr>
                    <ind left="400" hanging="200" firstLine="300" />
                </pPr>
                <r><t>c. AAC</t></r>
            </p>
            <p>
                <pPr>
                    <ind left="200" firstLine="400" />
                </pPr>
                <r><t>A. AACA</t></r>
            </p>
            <p>
                <pPr>
                    <ind left="100" firstLine="100" />
                </pPr>
                <r><t>d. AAD</t></r>
            </p>
            <p><r><t>2. AB</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AA
                    <ol class="pydocx-list-style-type-lowerLetter">
                        <li>AAA</li>
                        <li>AAB</li>
                        <li>AAC
                            <ol class="pydocx-list-style-type-upperLetter">
                                <li>AACA</li>
                            </ol>
                        </li>
                        <li>AAD</li>
                    </ol>
                </li>
                <li>AB</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_faked_list_that_skips_numbers(self):
        document_xml = '''
            <p><r><t>1. AA</t></r></p>
            <p><r><t>2. AB</t></r></p>
            <p><r><t>4. AC</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AA</li>
                <li>AB</li>
            </ol>
            <p>
                4. AC
            </p>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_faked_list_that_does_not_start_from_1(self):
        document_xml = '''
            <p><r><t>2. AA</t></r></p>
            <p><r><t>3. AB</t></r></p>
        '''

        expected_html = '''
            <p>2. AA</p>
            <p>3. AB</p>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_decimal_number_is_not_converted(self):
        document_xml = '''
            <p><r><t>1.1</t></r></p>
            <p><r><t>1.2</t></r></p>
        '''

        expected_html = '''
            <p>1.1</p>
            <p>1.2</p>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_space_after_dot_followed_by_number_is_converted(self):
        # This is like the decimal case, but there's a space after the dot
        document_xml = '''
            <p><r><t>1. 1</t></r></p>
            <p><r><t>2. 2</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>1</li>
                <li>2</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_space_required_after_digit_dot(self):
        document_xml = '''
            <p><r><t>1.a</t></r></p>
            <p><r><t>a</t><t>.b</t></r></p>
            <p><r><t>A</t><t>.</t><t>c</t></r></p>
            <p><r><t>I.</t><t>d</t></r></p>
            <p><r><t>i.e</t></r></p>
        '''

        expected_html = '''
            <p>1.a</p>
            <p>a.b</p>
            <p>A.c</p>
            <p>I.d</p>
            <p>i.e</p>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_tab_char_is_sufficient_for_space_after_dot(self):
        document_xml = '''
            <p><r><t>1.</t><tab /><t>a</t></r></p>
            <p><r><t>a.</t><tab /><t>b</t></r></p>
            <p><r><t>A.</t><tab /><t>c</t></r></p>
            <p><r><t>I.</t><tab /><t>d</t></r></p>
            <p><r><t>i.</t><tab /><t>e</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>a</li>
            </ol>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>b</li>
            </ol>
            <ol class="pydocx-list-style-type-upperLetter">
                <li>c</li>
            </ol>
            <ol class="pydocx-list-style-type-upperRoman">
                <li>d</li>
            </ol>
            <ol class="pydocx-list-style-type-lowerRoman">
                <li>e</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_single_item_lists(self):
        document_xml = '''
            <p><r><t>1. a</t></r></p>
            <p><r><t>a. b</t></r></p>
            <p><r><t>A. c</t></r></p>
            <p><r><t>I. d</t></r></p>
            <p><r><t>i. e</t></r></p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>a</li>
            </ol>
            <ol class="pydocx-list-style-type-lowerLetter">
                <li>b</li>
            </ol>
            <ol class="pydocx-list-style-type-upperLetter">
                <li>c</li>
            </ol>
            <ol class="pydocx-list-style-type-upperRoman">
                <li>d</li>
            </ol>
            <ol class="pydocx-list-style-type-lowerRoman">
                <li>e</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_trailing_text_is_not_removed(self):
        document_xml = '''
            <p>
                <r>
                    <t>1.</t>
                    <t> Foo </t>
                    <t>Bar</t>
                </r>
            </p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>Foo Bar</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_leading_text_is_not_removed(self):
        document_xml = '''
            <p>
                <r>
                    <t>1.</t>
                    <t> Foo</t>
                    <t> Bar</t>
                </r>
            </p>
        '''

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>Foo Bar</li>
            </ol>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_faked_list_with_list_level_numfmt_None_still_detected(self):
        document_xml = '''
            {aaa}
            {bbb}
        '''.format(
            aaa=self.simple_list_item.format(
                content='1. AAA',
                num_id=1,
                ilvl=0,
            ),
            bbb=self.simple_list_item.format(
                content='2. BBB',
                num_id=1,
                ilvl=0,
            ),
        )

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="none"/>
                </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AAA</li>
                <li>BBB</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_faked_within_a_table(self):
        document_xml = '''
            <tbl>
              <tr>
                <tc>
                  <p>
                    <r>
                      <t>1. Foo</t>
                    </r>
                  </p>
                  <p>
                    <r>
                      <t>2. Bar</t>
                    </r>
                  </p>
                </tc>
              </tr>
            </tbl>
        '''

        expected_html = '''
            <table border="1">
                <tr>
                    <td>
                        <ol class="pydocx-list-style-type-decimal">
                            <li>Foo</li>
                            <li>Bar</li>
                        </ol>
                    </td>
                </tr>
            </table>
        '''

        self.assert_main_document_xml_generates_html(document_xml, expected_html)


class FakedNumberingPatternBase(object):
    def assert_html_using_pattern(self, pattern):
        document_xml_format = [
            pattern.format(digit)
            for digit in self.document_xml_sequence
        ]
        document_xml = self.document_xml.format(*document_xml_format)
        expected_html = self.expected_html.format(*self.expected_html_format)
        self.assert_main_document_xml_generates_html(document_xml, expected_html)

    def test_format_digit_dot_space(self):
        self.assert_html_using_pattern('{0}. ')

    def test_digit_paren(self):
        self.assert_html_using_pattern('{0})')

    def test_digit_paren_with_spaces(self):
        self.assert_html_using_pattern(' {0}  )  ')

    def test_paren_digit_paren(self):
        self.assert_html_using_pattern('({0})')

    def test_paren_digit_paren_with_spaces(self):
        self.assert_html_using_pattern('  (  {0}  )  ')

    def test_format_digit_dot_with_spacing(self):
        self.assert_html_using_pattern('  {0}  .  ')


class PyDocXHTMLExporterNoStyleBaseNumberingSpan(PyDocXHTMLExporterNoStyle):
    numbering_span_builder_class = BaseNumberingSpanBuilder


class FakedNumberingDetectionDisabledBase(FakedNumberingPatternBase):
    def setUp(self):
        super(FakedNumberingDetectionDisabledBase, self).setUp()

        self.document_xml = '''
            <p><r><t>{0}AA</t></r></p>
            <p><r><t>{1}AB</t></r></p>
            <p><r>
                <tab />
                <t>{2}ABA</t>
            </r></p>
            <p><r>
                <tab />
                <t>{3}ABB</t>
            </r></p>
            <p><r><t>{4}AC</t></r></p>
        '''

        self.expected_html = '''
            <p>{0}AA</p>
            <p>{1}AB</p>
            <p>
                <span class="pydocx-tab"></span>{2}ABA
            </p>
            <p>
                <span class="pydocx-tab"></span>{3}ABB
            </p>
            <p>{4}AC</p>
        '''

    def assert_html_using_pattern(self, pattern):
        document_xml_format = [
            pattern.format(digit)
            for digit in self.document_xml_sequence
        ]
        document_xml = self.document_xml.format(*document_xml_format)
        expected_html = self.expected_html.format(*document_xml_format)
        self.assert_main_document_xml_generates_html(document_xml, expected_html)


class FakedNestedDecimalDisabledTestCase(
    FakedNumberingDetectionDisabledBase,
    DocumentGeneratorTestCase,
):
    exporter = PyDocXHTMLExporterNoStyleBaseNumberingSpan
    document_xml_sequence = [1, 2, 1, 2, 3]


class FakedNestedLowerLetterDisabledTestCase(
    FakedNumberingDetectionDisabledBase,
    DocumentGeneratorTestCase,
):
    exporter = PyDocXHTMLExporterNoStyleBaseNumberingSpan
    document_xml_sequence = ['a', 'b', 'a', 'b', 'c']


class FakedNestedUpperLetterDisabledTestCase(
    FakedNumberingDetectionDisabledBase,
    DocumentGeneratorTestCase,
):
    exporter = PyDocXHTMLExporterNoStyleBaseNumberingSpan
    document_xml_sequence = ['A', 'B', 'A', 'B', 'C']


class FakedNestedLowerRomanDisabledTestCase(
    FakedNumberingDetectionDisabledBase,
    DocumentGeneratorTestCase,
):
    exporter = PyDocXHTMLExporterNoStyleBaseNumberingSpan
    document_xml_sequence = ['i', 'ii', 'i', 'ii', 'iii']


class FakedNestedUpperRomanDisabledTestCase(
    FakedNumberingDetectionDisabledBase,
    DocumentGeneratorTestCase,
):
    exporter = PyDocXHTMLExporterNoStyleBaseNumberingSpan
    document_xml_sequence = ['I', 'II', 'I', 'II', 'III']


class FakedNestedNoContentBase(FakedNumberingPatternBase):
    def setUp(self):
        super(FakedNestedNoContentBase, self).setUp()

        self.document_xml = '''
            <p><r><t>{0}</t></r></p>
            <p><r><t>{1}</t></r></p>
            <p><r>
                <tab />
                <t>{2}</t>
            </r></p>
            <p><r>
                <tab />
                <t>{3}</t>
            </r></p>
            <p><r><t>{4}</t></r></p>
        '''

        self.expected_html = '''
            <ol class="pydocx-list-style-type-{0}">
                <li></li>
                <li>
                    <ol class="pydocx-list-style-type-{1}">
                        <li></li>
                        <li></li>
                    </ol>
                </li>
                <li></li>
            </ol>
        '''


class FakedNestedDecimalNoContentTestCase(
    FakedNestedNoContentBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['decimal', 'decimal']
    document_xml_sequence = [1, 2, 1, 2, 3]


class FakedNestedLowerLetterNoContentTestCase(
    FakedNestedNoContentBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['lowerLetter', 'lowerLetter']
    document_xml_sequence = ['a', 'b', 'a', 'b', 'c']


class FakedNestedUpperLetterNoContentTestCase(
    FakedNestedNoContentBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['upperLetter', 'upperLetter']
    document_xml_sequence = ['A', 'B', 'A', 'B', 'C']


class FakedNestedLowerRomanNoContentTestCase(
    FakedNestedNoContentBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['lowerRoman', 'lowerRoman']
    document_xml_sequence = ['i', 'ii', 'i', 'ii', 'iii']


class FakedNestedUpperRomanNoContentTestCase(
    FakedNestedNoContentBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['upperRoman', 'upperRoman']
    document_xml_sequence = ['I', 'II', 'I', 'II', 'III']


class FakedNestedNumberingPatternBase(FakedNumberingPatternBase):
    def setUp(self):
        super(FakedNestedNumberingPatternBase, self).setUp()

        self.document_xml = '''
            <p><r><t>{0}AA</t></r></p>
            <p><r><t>{1}AB</t></r></p>
            <p><r>
                <tab />
                <t>{2}ABA</t>
            </r></p>
            <p><r>
                <tab />
                <t>{3}ABB</t>
            </r></p>
            <p><r>
                <tab />
                <tab />
                <t>{4}ABBA</t>
            </r></p>
            <p><r>
                <tab />
                <tab />
                <t>{5}ABBB</t>
            </r></p>
            <p>
                <pPr>
                    <ind left="1440" />
                </pPr>
                <r><t>{6}ABBC</t></r>
            </p>
            <p><r>
                <tab />
                <t>{7}ABC</t>
            </r></p>
            <p><r><t>{8}AC</t></r></p>
        '''

        self.expected_html = '''
            <ol class="pydocx-list-style-type-{0}">
                <li>AA</li>
                <li>AB
                    <ol class="pydocx-list-style-type-{1}">
                        <li>ABA</li>
                        <li>ABB
                            <ol class="pydocx-list-style-type-{2}">
                                <li>ABBA</li>
                                <li>ABBB</li>
                                <li>ABBC</li>
                            </ol>
                        </li>
                        <li>ABC</li>
                    </ol>
                </li>
                <li>AC</li>
            </ol>
        '''


class FakedNestedDecimalTestCase(
    FakedNestedNumberingPatternBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['decimal', 'decimal', 'decimal']
    document_xml_sequence = [1, 2, 1, 2, 1, 2, 3, 3, 3]


class FakedNestedLowerLetterTestCase(
    FakedNestedNumberingPatternBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['lowerLetter', 'lowerLetter', 'lowerLetter']
    document_xml_sequence = ['a', 'b', 'a', 'b', 'a', 'b', 'c', 'c', 'c']


class FakedNestedUpperLetterTestCase(
    FakedNestedNumberingPatternBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['upperLetter', 'upperLetter', 'upperLetter']
    document_xml_sequence = ['A', 'B', 'A', 'B', 'A', 'B', 'C', 'C', 'C']


class FakedNestedLowerRomanTestCase(
    FakedNestedNumberingPatternBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['lowerRoman', 'lowerRoman', 'lowerRoman']
    document_xml_sequence = ['i', 'ii', 'i', 'ii', 'i', 'ii', 'iii', 'iii', 'iii']


class FakedNestedUpperRomanTestCase(
    FakedNestedNumberingPatternBase,
    DocumentGeneratorTestCase,
):
    expected_html_format = ['upperRoman', 'upperRoman', 'upperRoman']
    document_xml_sequence = ['I', 'II', 'I', 'II', 'I', 'II', 'III', 'III', 'III']
