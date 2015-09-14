# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.openxml.packaging import FootnotesPart, MainDocumentPart
from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory


class FootnoteTestCase(DocumentGeneratorTestCase):
    def test_footnote_without_definition_is_ignored(self):
        document_xml = '''
            <p>
              <r>
                <t>Foo</t>
              </r>
              <r>
                <footnoteReference id="abc"/>
              </r>
            </p>
        '''
        document = WordprocessingDocumentFactory()
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>Foo</p>'
        self.assert_document_generates_html(document, expected_html)

    def test_basic_footnote_with_styling(self):
        document_xml = '''
            <p>
              <r>
                <t>Foo</t>
              </r>
              <r>
                <rPr>
                  <vertAlign val="superscript"/>
                </rPr>
                <footnoteReference id="abc"/>
              </r>
            </p>
            <p>
              <r>
                <t>Footnotes should appear below this</t>
              </r>
            </p>
        '''

        footnotes_xml = '''
            <footnote id="abc">
              <p>
                <r>
                  <rPr>
                    <b val="on"/>
                  </rPr>
                  <footnoteRef/>
                  <t>Bar</t>
                </r>
              </p>
            </footnote>
        '''

        document = WordprocessingDocumentFactory()
        document.add(FootnotesPart, footnotes_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                Foo
                <sup>
                    <a href="#footnote-abc" name="footnote-ref-abc">1</a>
                </sup>
            </p>
            <p>Footnotes should appear below this</p>
            <hr />
            <ol class="pydocx-list-style-type-decimal">
                <li><p><strong>
                    <a href="#footnote-ref-abc" name="footnote-abc">^</a>
                    Bar
                </strong></p></li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_footnote_with_hyperlink(self):
        document_xml = '''
            <p>
              <r>
                <t>Foo</t>
              </r>
              <r>
                <rPr>
                  <vertAlign val="superscript"/>
                </rPr>
                <footnoteReference id="abc"/>
              </r>
            </p>
            <p>
              <r>
                <t>Footnotes should appear below this</t>
              </r>
            </p>
        '''

        footnotes_xml = '''
            <footnote id="abc">
              <p>
                <r>
                  <footnoteRef/>
                </r>
                <hyperlink id="foobar">
                  <r>
                    <t>Bar</t>
                  </r>
                </hyperlink>
              </p>
            </footnote>
        '''

        document = WordprocessingDocumentFactory()

        footnotes_rels = document.relationship_format.format(
            id='foobar',
            type='foo/hyperlink',
            target='http://google.com',
            target_mode='External',
        )

        document.add(FootnotesPart, footnotes_xml, footnotes_rels)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                Foo
                <sup>
                    <a href="#footnote-abc" name="footnote-ref-abc">1</a>
                </sup>
            </p>
            <p>Footnotes should appear below this</p>
            <hr />
            <ol class="pydocx-list-style-type-decimal">
                <li>
                    <p>
                        <a href="#footnote-ref-abc" name="footnote-abc">^</a>
                        <a href="http://google.com">Bar</a>
                    </p>
                </li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)

    def test_multiple_footnotes_defined_in_a_order_different_from_usage(self):
        document_xml = '''
            <p>
              <r>
                <t>Foo</t>
              </r>
              <r>
                <rPr>
                  <vertAlign val="superscript"/>
                </rPr>
                <footnoteReference id="one"/>
              </r>
              <r>
                <t>Bar</t>
              </r>
              <r>
                <rPr>
                  <vertAlign val="superscript"/>
                </rPr>
                <footnoteReference id="two"/>
              </r>
              <r>
                <t>Baz</t>
              </r>
              <r>
                <rPr>
                  <vertAlign val="superscript"/>
                </rPr>
                <footnoteReference id="three"/>
              </r>
            </p>
            <p>
              <r>
                <t>Footnotes should appear below this</t>
              </r>
            </p>
        '''

        footnotes_xml = '''
            <footnote id="two">
              <p>
                <r>
                  <footnoteRef/>
                  <t>Beta</t>
                </r>
              </p>
            </footnote>
            <footnote id="three">
              <p>
                <r>
                  <footnoteRef/>
                  <t>Gamma</t>
                </r>
              </p>
            </footnote>
            <footnote id="one">
              <p>
                <r>
                  <footnoteRef/>
                  <t>Alpha</t>
                </r>
              </p>
            </footnote>
        '''

        document = WordprocessingDocumentFactory()
        document.add(FootnotesPart, footnotes_xml)
        document.add(MainDocumentPart, document_xml)

        expected_html = '''
            <p>
                Foo
                <sup>
                    <a href="#footnote-one" name="footnote-ref-one">1</a>
                </sup>
                Bar
                <sup>
                    <a href="#footnote-two" name="footnote-ref-two">2</a>
                </sup>
                Baz
                <sup>
                    <a href="#footnote-three" name="footnote-ref-three">3</a>
                </sup>
            </p>
            <p>Footnotes should appear below this</p>
            <hr />
            <ol class="pydocx-list-style-type-decimal">
                <li><p>
                    <a href="#footnote-ref-one" name="footnote-one">^</a>
                    Alpha
                </p></li>
                <li><p>
                    <a href="#footnote-ref-two" name="footnote-two">^</a>
                    Beta
                </p></li>
                <li><p>
                    <a href="#footnote-ref-three" name="footnote-three">^</a>
                    Gamma
                </p></li>
            </ol>
        '''
        self.assert_document_generates_html(document, expected_html)
