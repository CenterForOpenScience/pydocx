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
            <h1>foo</h1>
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
            <h1>foo</h1>
            <p>bare paragraph</p>
            <h1>bar</h1>
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
