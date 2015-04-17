# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.wordml import MainDocumentPart, StyleDefinitionsPart


class FakedSubScriptTestCase(DocumentGeneratorTestCase):
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


class FakedSuperScriptTestCase(DocumentGeneratorTestCase):
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


class PageBreakTestCase(DocumentGeneratorTestCase):
    def test_before_text_run(self):
        document_xml = '''
            <p>
              <r>
                <t>aaa</t>
              </r>
            </p>
            <p>
              <r>
                <br type="page"/>
                <t>bbb</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa</p><p><hr />bbb</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_between_paragraphs(self):
        document_xml = '''
            <p>
              <r>
                <t>aaa</t>
              </r>
            </p>
            <p>
              <r>
                <br type="page"/>
              </r>
            </p>
            <p>
              <r>
                <t>bbb</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa</p><p><hr /></p><p>bbb</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_after_text_run(self):
        document_xml = '''
            <p>
              <r>
                <t>aaa</t>
                <br type="page"/>
              </r>
            </p>
            <p>
              <r>
                <t>bbb</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa<hr /></p><p>bbb</p>'
        self.assert_document_generates_html(document, expected_html)


class PropertyHierarchyTestCase(DocumentGeneratorTestCase):
    def test_local_character_style(self):
        document_xml = '''
            <p>
              <r>
                <rPr>
                  <b val="on"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><strong>aaa</strong></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_global_run_character_style(self):
        style_xml = '''
            <style styleId="foo" type="character">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <r>
                <rPr>
                  <rStyle val="foo"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><strong>aaa</strong></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_global_run_paragraph_style(self):
        style_xml = '''
            <style styleId="foo" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><strong>aaa</strong></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_global_run_paragraph_and_character_styles(self):
        style_xml = '''
            <style styleId="foo" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
            <style styleId="bar" type="character">
              <rPr>
                <i val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <rPr>
                  <rStyle val="bar"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><em><strong>aaa</strong></em></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_local_styles_override_global_styles(self):
        style_xml = '''
            <style styleId="foo" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
            <style styleId="bar" type="character">
              <rPr>
                <i val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <rPr>
                  <rStyle val="bar"/>
                  <b val="off"/>
                  <i val="off"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_paragraph_style_referenced_by_run_is_ignored(self):
        style_xml = '''
            <style styleId="foo" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <r>
                <rPr>
                  <rStyle val="foo"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_character_style_referenced_by_paragraph_is_ignored(self):
        style_xml = '''
            <style styleId="foo" type="character">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_run_paragraph_mark_style_is_not_used_as_run_style(self):
        style_xml = '''
            <style styleId="foo" type="paragraph">
              <pPr>
                <rPr>
                  <b val="on"/>
                </rPr>
              </pPr>
            </style>
        '''

        document_xml = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''

        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>aaa</p>'
        self.assert_document_generates_html(document, expected_html)
