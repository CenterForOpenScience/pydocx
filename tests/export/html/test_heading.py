# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging import (
    MainDocumentPart,
    NumberingDefinitionsPart,
    StyleDefinitionsPart,
)
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class HeadingTestCase(DocumentGeneratorTestCase):
    def test_character_stylings_are_ignored(self):
        # Even though the heading1 style has bold enabled, it's being ignored
        # because the style is for a header
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="heading1"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <h1>aaa</h1>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_each_heading_level(self):
        style_template = '''
            <style styleId="heading%s" type="paragraph">
              <name val="Heading %s"/>
            </style>
        '''

        style_xml = ''.join(
            style_template % (i, i)
            for i in range(1, 11)
        )

        paragraph_template = '''
            <p>
              <pPr>
                <pStyle val="%s"/>
              </pPr>
              <r>
                <t>%s</t>
              </r>
            </p>
        '''

        style_to_text = [
            ('heading1', 'aaa'),
            ('heading2', 'bbb'),
            ('heading3', 'ccc'),
            ('heading4', 'ddd'),
            ('heading5', 'eee'),
            ('heading6', 'fff'),
            ('heading7', 'ggg'),
            ('heading8', 'hhh'),
            ('heading9', 'iii'),
            ('heading10', 'jjj'),
        ]

        document_xml = ''.join(
            paragraph_template % entry
            for entry in style_to_text
        )

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <h1>aaa</h1>
            <h2>bbb</h2>
            <h3>ccc</h3>
            <h4>ddd</h4>
            <h5>eee</h5>
            <h6>fff</h6>
            <h6>ggg</h6>
            <h6>hhh</h6>
            <h6>iii</h6>
            <h6>jjj</h6>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_has_precedence_over_list_single_lvl(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>
                    <strong>foo</strong>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_in_sub_list(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="lowerLetter"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="1" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>bar</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>
                    foo
                    <ol class="pydocx-list-style-type-lowerLetter">
                        <li>
                            <strong>bar</strong>
                        </li>
                    </ol>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_in_nested_sub_list(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
                <lvl ilvl="1">
                    <numFmt val="lowerLetter"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
            <p>
              <pPr>
                <numPr>
                    <ilvl val="1" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>bar</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="2" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>baz</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                    <li>
                            foo
                            <ol class="pydocx-list-style-type-lowerLetter">
                                    <li>bar</li>
                            </ol>
                    </li>
            </ol>
            <h1>baz</h1>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_in_list_with_bare_paragraph(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
            <p><r><t>bare paragraph</t></r></p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>bar</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>
                    <strong>foo</strong>
                    <br />
                    bare paragraph
                </li>
                <li>
                    <strong>bar</strong>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_in_table_cell(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        document_xml = '''
            <tbl>
                <tr>
                    <tc>
                        <p>
                          <pPr>
                            <pStyle val="heading1"/>
                            <numPr>
                                <ilvl val="0" />
                                <numId val="1" />
                            </numPr>
                          </pPr>
                          <r>
                            <t>foo</t>
                          </r>
                        </p>
                    </tc>
                </tr>
            </tbl>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <table border="1">
                <tr>
                    <td><h1>foo</h1></td>
                </tr>
            </table>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_as_new_list_following_bare_paragraph_plus_list(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
            <num numId="2">
                <abstractNumId val="2"/>
            </num>
            <abstractNum abstractNumId="2">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
            <p><r><t>bare paragraph</t></r></p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="2" />
                </numPr>
              </pPr>
              <r>
                <t>bar</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>foo</li>
            </ol>
            <p>bare paragraph</p>
            <ol class="pydocx-list-style-type-decimal">
                <li><strong>bar</strong></li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_as_list_following_bare_paragraph_plus_list(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
            <p><r><t>bare paragraph</t></r></p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>bar</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>foo<br />bare paragraph</li>
                <li><strong>bar</strong></li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_list_heading_table_paragraph(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <numPr>
                  <ilvl val="0"/>
                  <numId val="1"/>
                </numPr>
              </pPr>
              <r>
                <t>single list item</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
              </pPr>
              <r>
                <t>actual heading</t>
              </r>
            </p>
            <p>
              <r>
                <t>before table</t>
              </r>
            </p>
            <tbl>
              <tr>
                <tc>
                  <p>
                    <r>
                      <t>foo</t>
                    </r>
                  </p>
                </tc>
              </tr>
            </tbl>
            <p>
              <r>
                <t>after table</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>single list item</li>
            </ol>
            <h1>actual heading</h1>
            <p>before table</p>
            <table border="1">
                <tr>
                    <td>foo</td>
                </tr>
            </table>
            <p>after table</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_heading_has_precedence_over_list_single_lvl_multiple_items(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
        '''

        numbering_xml = '''
            <num numId="1">
                <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
                <lvl ilvl="0">
                    <numFmt val="decimal"/>
                </lvl>
            </abstractNum>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>foo</t>
              </r>
            </p>
            <p>
              <pPr>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>non-heading list item</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading1"/>
                <numPr>
                    <ilvl val="0" />
                    <numId val="1" />
                </numPr>
              </pPr>
              <r>
                <t>bar</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li><strong>foo</strong></li>
                <li>non-heading list item</li>
                <li><strong>bar</strong></li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)
