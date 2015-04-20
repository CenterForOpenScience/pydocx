# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart, StyleDefinitionsPart


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
