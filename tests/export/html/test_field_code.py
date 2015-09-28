# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.openxml.packaging import MainDocumentPart, StyleDefinitionsPart
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
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> FOOBAR baz</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(StyleDefinitionsPart, style_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <h1>AAA</h1>
        '''
        self.assert_document_generates_html(document, expected_html)


class FieldCodeTestCase(DocumentGeneratorTestCase):
    def test_unsupported_instr_content_is_not_ignored(self):
        document_xml = '''
            <p>
                <r><t>AAA</t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> FOOBAR baz</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>BBB</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>CCC</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>AAABBBCCC</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_multiple_instr_with_same_paragraph_parent(self):
        document_xml = '''
            <p>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> FOOBAR baz</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>BBB</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r>
                    <t>CCC</t>
                </r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> FOOBAR baz</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>DDD</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r>
                    <t>EEE</t>
                </r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>AAABBBCCCDDDEEE</p>'
        self.assert_document_generates_html(document, expected_html)


class HyperlinkTestCase(DocumentGeneratorTestCase):
    def test_spanning_single_paragraph(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "http://www.google.com/"</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Link: <a href="http://www.google.com/">AAA</a>.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_spanning_multiple_paragraphs(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
            </p>
            <p>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "http://www.google.com/"</instrText>
                </r>
            </p>
            <p>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <t>BBB</t>
                </r>
            </p>
            <p><r><t>CCC</t></r></p>
            <p>
                <r><t>DDD</t></r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>Link: </p>
            <p><a href="http://www.google.com/">AAABBB</a></p>
            <p><a href="http://www.google.com/">CCC</a></p>
            <p><a href="http://www.google.com/">DDD</a>.</p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_missing_fld_char_end(self):
        # According to 17.16.18, "If a complex field is not closed before the
        # end of a document story, then no field shall be generated and each
        # individual run shall be processed as if the field characters did not
        # exist"
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "http://www.google.com/"</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Link: AAA.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_begin_without_end_before_next_begin(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "http://www.google.com"</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r><t>.</t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "http://www.facebook.com/"</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>BBB</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                Link: AAA.
                <a href="http://www.facebook.com/">BBB</a>.
            </p>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_instr_missing_target(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK </instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Link: AAA.</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_with_bookmark_option(self):
        document_xml = '''
            <p>
                <r><t>Link: </t></r>
                <r>
                    <fldChar fldCharType="begin"/>
                </r>
                <r>
                    <instrText> HYPERLINK "http://www.google.com/" \\l awesome</instrText>
                </r>
                <r>
                    <fldChar fldCharType="separate"/>
                </r>
                <r>
                    <t>AAA</t>
                </r>
                <r>
                    <fldChar fldCharType="end"/>
                </r>
                <r><t>.</t></r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Link: <a href="http://www.google.com/#awesome">AAA</a>.</p>'
        self.assert_document_generates_html(document, expected_html)
