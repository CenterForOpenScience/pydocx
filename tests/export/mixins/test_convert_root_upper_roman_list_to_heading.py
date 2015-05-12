# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export.html import PyDocXHTMLExporter
from pydocx.export.mixins import ConvertRootUpperRomanListToHeadingMixin
from pydocx.test import DocumentGeneratorTestCase, DocXFixtureTestCaseFactory
from pydocx.test.utils import (
    PyDocXHTMLExporterNoStyle,
    WordprocessingDocumentFactory,
)
from pydocx.openxml.packaging import MainDocumentPart, NumberingDefinitionsPart


class ConvertRootUpperRomanListToHeadingExporterNoStyle(
    ConvertRootUpperRomanListToHeadingMixin,
    PyDocXHTMLExporterNoStyle,
):
    pass


class ConvertRootUpperRomanListToHeadingExporter(
    ConvertRootUpperRomanListToHeadingMixin,
    PyDocXHTMLExporter,
):
    pass


class ConvertRootUpperRomanListToHeadingTestCase(DocumentGeneratorTestCase):
    exporter = ConvertRootUpperRomanListToHeadingExporterNoStyle
    list_item = '''
        <p>
          <pPr>
            <numPr>
              <ilvl val="{level}"/>
              <numId val="{num_id}"/>
            </numPr>
          </pPr>
          <r><t>{content}</t></r>
        </p>
    '''

    def test_only_root_level_upperRoman_list_converted_to_heading(self):
        document_xml = ''.join([
            self.list_item.format(
                content='AAA',
                num_id=1,
                level=0,
            ),
            self.list_item.format(
                content='BBB',
                num_id=1,
                level=1,
            ),
            self.list_item.format(
                content='CCC',
                num_id=1,
                level=2,
            ),
        ])

        numbering_xml = '''
            <num numId="1">
              <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
              <lvl ilvl="0">
                <numFmt val="upperRoman"/>
              </lvl>
              <lvl ilvl="1">
                <numFmt val="decimal"/>
              </lvl>
              <lvl ilvl="2">
                <numFmt val="upperRoman"/>
              </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <h2>AAA</h2>
            <ol class="pydocx-list-style-type-decimal">
                <li>BBB
                    <ol class="pydocx-list-style-type-upperRoman">
                        <li>CCC</li>
                    </ol>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_missing_numbering_definition(self):
        document_xml = ''.join([
            self.list_item.format(
                content='AAA',
                num_id=1,
                level=0,
            ),
        ])

        numbering_xml = ''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-None">
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_missing_numbering_part(self):
        document_xml = ''.join([
            self.list_item.format(
                content='AAA',
                num_id=1,
                level=0,
            ),
        ])

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>AAA</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_missing_level_definition(self):
        document_xml = ''.join([
            self.list_item.format(
                content='AAA',
                num_id=1,
                level=0,
            ),
        ])

        numbering_xml = '''
            <num numId="1">
              <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-None">
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_root_level_upperRoman_list_not_converted_to_heading(self):
        document_xml = ''.join([
            self.list_item.format(
                content='AAA',
                num_id=1,
                level=0,
            ),
        ])

        numbering_xml = '''
            <num numId="1">
              <abstractNumId val="1"/>
            </num>
            <abstractNum abstractNumId="1">
              <lvl ilvl="0">
                <numFmt val="upperRoman"/>
              </lvl>
            </abstractNum>
        '''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<h2>AAA</h2>'
        self.assert_document_generates_html(document, expected_html)

    def test_root_level_decimal_list_not_converted_to_heading(self):
        document_xml = ''.join([
            self.list_item.format(
                content='AAA',
                num_id=1,
                level=0,
            ),
        ])

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

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <ol class="pydocx-list-style-type-decimal">
                <li>AAA</li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_without_properties_is_not_converted(self):
        document_xml = '<p><r><t>Foo</t></r></p>'

        numbering_xml = ''

        document = WordprocessingDocumentFactory()
        document.add(NumberingDefinitionsPart, numbering_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Foo</p>'
        self.assert_document_generates_html(document, expected_html)


class DocXFixtureTestCase(DocXFixtureTestCaseFactory):
    exporter = ConvertRootUpperRomanListToHeadingExporter
    cases = (
        # The list element GGG is expected to be upperRoman.
        # This demonstrates that ONLY top-level / root upperRoman's are
        # converted
        'list_to_header',
    )

DocXFixtureTestCase.generate()
