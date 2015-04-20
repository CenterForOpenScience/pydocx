# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export.html import PyDocXHTMLExporter
from pydocx.export.mixins import FakedSuperscriptAndSubscriptExportMixin
from pydocx.test import DocumentGeneratorTestCase, DocXFixtureTestCaseFactory
from pydocx.test.utils import (
    PyDocXHTMLExporterNoStyle,
    WordprocessingDocumentFactory,
)
from pydocx.openxml.packaging import MainDocumentPart, StyleDefinitionsPart


class FakedSuperscriptAndSubscriptHTMLExporterNoStyle(
    FakedSuperscriptAndSubscriptExportMixin,
    PyDocXHTMLExporterNoStyle,
):
    pass


class FakedSuperscriptAndSubscriptHTMLExporter(
    FakedSuperscriptAndSubscriptExportMixin,
    PyDocXHTMLExporter,
):
    pass


class FakedSuperscriptAndSubscriptTestCase(DocumentGeneratorTestCase):
    exporter = FakedSuperscriptAndSubscriptHTMLExporterNoStyle


class FakedSubScriptTestCase(FakedSuperscriptAndSubscriptTestCase):
    style_xml = '''
        <style styleId="faked_subscript" type="paragraph">
          <name val="Normal"/>
          <rPr>
            <sz val="24"/>
          </rPr>
        </style>
    '''

    def test_sub_detected_pStyle_has_smaller_size_and_negative_position(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_subscript"/>
              </pPr>
              <r>
                <t>H</t>
              </r>
              <r>
                <rPr>
                  <position val="-8"/>
                  <sz val="19"/>
                </rPr>
                <t>2</t>
              </r>
              <r>
                <t>O</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>H<sub>2</sub>O</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sub_detected_because_local_size_larger_than_pStyle_size(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_subscript"/>
              </pPr>
              <r>
                <t>H</t>
              </r>
              <r>
                <rPr>
                  <position val="-8"/>
                  <sz val="30"/>
                </rPr>
                <t>2</t>
              </r>
              <r>
                <t>O</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>H2O</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sub_because_position_is_zero(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_subscript"/>
              </pPr>
              <r>
                <t>H</t>
              </r>
              <r>
                <rPr>
                  <position val="0"/>
                  <sz val="19"/>
                </rPr>
                <t>2</t>
              </r>
              <r>
                <t>O</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>H2O</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sub_because_position_is_not_set(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_subscript"/>
              </pPr>
              <r>
                <t>H</t>
              </r>
              <r>
                <rPr>
                  <sz val="19"/>
                </rPr>
                <t>2</t>
              </r>
              <r>
                <t>O</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>H2O</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sub_detected_for_size_set_in_rPrChange(self):
        # Test for issue #116
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_subscript"/>
              </pPr>
              <r>
                <t>H</t>
              </r>
              <r>
                <rPr>
                  <position val="-8"/>
                  <rPrChange id="1" author="john" date="2015-02-10T14:33:00Z">
                    <sz val="19"/>
                  </rPrChange>
                </rPr>
                <t>2</t>
              </r>
              <r>
                <t>O</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>H2O</p>'
        self.assert_document_generates_html(document, expected_html)


class FakedSuperScriptTestCase(FakedSuperscriptAndSubscriptTestCase):
    style_xml = '''
        <style styleId="faked_superscript" type="paragraph">
          <name val="Normal"/>
          <rPr>
            <sz val="24"/>
          </rPr>
        </style>
    '''

    def test_sup_detected_pStyle_has_larger_size_and_positive_position(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_superscript"/>
              </pPr>
              <r>
                <t>n</t>
              </r>
              <r>
                <rPr>
                  <position val="8"/>
                  <sz val="19"/>
                </rPr>
                <t>th</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>n<sup>th</sup></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sup_detected_because_local_size_larger_than_pStyle_size(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_superscript"/>
              </pPr>
              <r>
                <t>n</t>
              </r>
              <r>
                <rPr>
                  <position val="8"/>
                  <sz val="30"/>
                </rPr>
                <t>th</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>nth</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sup_because_position_is_zero(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_superscript"/>
              </pPr>
              <r>
                <t>n</t>
              </r>
              <r>
                <rPr>
                  <position val="0"/>
                  <sz val="19"/>
                </rPr>
                <t>th</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>nth</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sup_because_position_is_not_set(self):
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_superscript"/>
              </pPr>
              <r>
                <t>n</t>
              </r>
              <r>
                <rPr>
                  <sz val="19"/>
                </rPr>
                <t>th</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>nth</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_no_sup_detected_for_size_set_in_rPrChange(self):
        # Test for issue #116
        document_xml = '''
            <p>
              <pPr>
                <pStyle val="faked_superscript"/>
              </pPr>
              <r>
                <t>n</t>
              </r>
              <r>
                <rPr>
                  <position val="8"/>
                  <rPrChange id="1" author="john" date="2015-02-10T14:33:00Z">
                    <sz val="19"/>
                  </rPrChange>
                </rPr>
                <t>th</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, self.style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>nth</p>'
        self.assert_document_generates_html(document, expected_html)


class DocXFixtureTestCase(DocXFixtureTestCaseFactory):
    exporter = FakedSuperscriptAndSubscriptHTMLExporter
    cases = (
        'fake_subscript',
        'fake_superscript',
    )

DocXFixtureTestCase.generate()
