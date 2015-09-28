# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase


from pydocx.openxml.packaging import MainDocumentPart, StyleDefinitionsPart
from pydocx.openxml.wordprocessing.simple_field import SimpleField
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class HeadingTestCase(DocumentGeneratorTestCase):
    def test_styles_are_ignored(self):
        style_xml = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
              <rPr>
                <b val="on"/>
                <caps val="on"/>
                <smallCaps val="on"/>
                <strike val="on"/>
                <dstrike val="on"/>
              </rPr>
            </style>
        '''

        document_xml = '''
            <p>
                <pPr>
                    <pStyle val="heading1"/>
                </pPr>
                <fldSimple instr="FOO bar">
                    <r>
                        <t>AAA</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <h1>AAA</h1>
        '''
        self.assert_document_generates_html(document, expected_html)


class HyperlinkTestCase(DocumentGeneratorTestCase):
    def test_single_run(self):
        document_xml = '''
            <p>
                <fldSimple instr="HYPERLINK http://www.google.com">
                    <r>
                        <rPr>
                            <b />
                        </rPr>
                        <t>AAA</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                <a href="http://www.google.com">
                    <strong>AAA</strong>
                </a>
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_multiple_runs(self):
        document_xml = '''
            <p>
                <fldSimple instr="HYPERLINK http://www.google.com">
                    <r>
                        <rPr>
                            <b />
                        </rPr>
                        <t>AAA</t>
                    </r>
                    <r>
                        <rPr>
                            <i />
                        </rPr>
                        <t>BBB</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                <a href="http://www.google.com">
                    <strong>AAA</strong>
                    <em>BBB</em>
                </a>
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_instr_missing_target(self):
        document_xml = '''
            <p>
                <fldSimple instr="HYPERLINK ">
                    <r>
                        <rPr>
                            <b />
                        </rPr>
                        <t>AAA</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p><strong>AAA</strong></p>'
        self.assert_document_generates_html(document, expected_html)

    def test_with_bookmark_option(self):
        document_xml = '''
            <p>
                <fldSimple instr="HYPERLINK http://www.google.com \\l awesome">
                    <r>
                        <t>AAA</t>
                    </r>
                </fldSimple>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                <a href="http://www.google.com#awesome">AAA</a>
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)


class ParseInstrIntoFieldTypeAndArgStringTestCase(TestCase):
    def parse(self, instr):
        field = SimpleField(instr=instr)
        return field._parse_instr_into_field_type_and_arg_string()

    def test_with_blank_string_returns_None(self):
        result = self.parse('')
        self.assertEqual(result, None)

    def test_with_command_no_spaces_returns_command_and_empty_args(self):
        result = self.parse('COMMAND')
        self.assertEqual(result.groups(), ('COMMAND', ''))

    def test_with_command_with_spaces_returns_command_and_empty_args(self):
        result = self.parse('  COMMAND    ')
        self.assertEqual(result.groups(), ('COMMAND', ''))

    def test_command_with_spaces_and_args(self):
        result = self.parse('  COMMAND    foo bar  "hello   world" ')
        self.assertEqual(
            result.groups(),
            ('COMMAND', 'foo bar  "hello   world" '),
        )


class ParseInstrArgStringIntoArgsTestCase(TestCase):
    def parse(self, arg_string):
        field = SimpleField()
        return field._parse_instr_arg_string_to_args(arg_string)

    def test_with_blank_string_returns_empty_list(self):
        result = self.parse('')
        self.assertEqual(result, [])

    def test_single_word_with_spaces(self):
        result = self.parse('     foo   ')
        self.assertEqual(result, [('', 'foo')])

    def test_multiple_word_with_spaces(self):
        result = self.parse('     foo  bar  ')
        self.assertEqual(result, [('', 'foo'), ('', 'bar')])

    def test_multiple_words_with_quoted_phrase(self):
        result = self.parse('     foo  "hello world" bar')
        self.assertEqual(result, [('', 'foo'), ('hello world', ''), ('', 'bar')])


class ParseInstrTestCase(TestCase):
    def parse(self, instr):
        field = SimpleField(instr=instr)
        return field.parse_instr()

    def test_with_blank_instr_returns_None(self):
        result = self.parse('')
        self.assertEqual(result, None)

    def test_with_command(self):
        result = self.parse('COMMAND ')
        self.assertEqual(result, ('COMMAND', None))

    def test_with_command_with_args(self):
        result = self.parse('COMMAND foo "hello world" bar')
        self.assertEqual(result, ('COMMAND', ['foo', 'hello world', 'bar']))

    def test_with_command_and_only_quoted_arg(self):
        result = self.parse('COMMAND "foo hello  world bar"')
        self.assertEqual(result, ('COMMAND', ['foo hello  world bar']))
