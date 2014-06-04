from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.tests import DocumentGeneratorTestCase


class HeadingTestCase(DocumentGeneratorTestCase):
    def test_character_stylings_are_ignored(self):
        # Even though the heading1 style has bold enabled, it's being ignored
        # because the style is for a header
        style = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="heading1"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '''
            <h1>aaa</h1>
        '''
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_each_heading_level(self):
        style = '''
            <style styleId="heading1" type="paragraph">
              <name val="Heading 1"/>
            </style>
            <style styleId="heading2" type="paragraph">
              <name val="Heading 2"/>
            </style>
            <style styleId="heading3" type="paragraph">
              <name val="Heading 3"/>
            </style>
            <style styleId="heading4" type="paragraph">
              <name val="Heading 4"/>
            </style>
            <style styleId="heading5" type="paragraph">
              <name val="Heading 5"/>
            </style>
            <style styleId="heading6" type="paragraph">
              <name val="Heading 6"/>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="heading1"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading2"/>
              </pPr>
              <r>
                <t>bbb</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading3"/>
              </pPr>
              <r>
                <t>ccc</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading4"/>
              </pPr>
              <r>
                <t>ddd</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading5"/>
              </pPr>
              <r>
                <t>eee</t>
              </r>
            </p>
            <p>
              <pPr>
                <pStyle val="heading6"/>
              </pPr>
              <r>
                <t>fff</t>
              </r>
            </p>
        '''
        expected_html = '''
            <h1>aaa</h1>
            <h2>bbb</h2>
            <h3>ccc</h3>
            <h4>ddd</h4>
            <h5>eee</h5>
            <h6>fff</h6>
        '''
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )


class PageBreakTestCase(DocumentGeneratorTestCase):
    def test_before_text_run(self):
        xml_body = '''
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
        expected_html = '<p>aaa</p><p><hr />bbb</p>'
        self.assert_xml_body_matches_expected_html(xml_body, expected_html)

    def test_between_paragraphs(self):
        xml_body = '''
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
        expected_html = '<p>aaa</p><p><hr /></p><p>bbb</p>'
        self.assert_xml_body_matches_expected_html(xml_body, expected_html)

    def test_after_text_run(self):
        xml_body = '''
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
        expected_html = '<p>aaa<hr /></p><p>bbb</p>'
        self.assert_xml_body_matches_expected_html(xml_body, expected_html)


class PropertyHierarchyTestCase(DocumentGeneratorTestCase):
    def test_local_character_style(self):
        xml_body = '''
            <p>
              <r>
                <rPr>
                  <b val="on"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p><strong>aaa</strong></p>'
        self.assert_xml_body_matches_expected_html(xml_body, expected_html)

    def test_global_run_character_style(self):
        style = '''
            <style styleId="foo" type="character">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <r>
                <rPr>
                  <rStyle val="foo"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p><strong>aaa</strong></p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_global_run_paragraph_style(self):
        style = '''
            <style styleId="foo" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p><strong>aaa</strong></p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_global_run_paragraph_and_character_styles(self):
        style = '''
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

        xml_body = '''
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
        expected_html = '<p><em><strong>aaa</strong></em></p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_local_styles_override_global_styles(self):
        style = '''
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

        xml_body = '''
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
        expected_html = '<p>aaa</p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_paragraph_style_referenced_by_run_is_ignored(self):
        style = '''
            <style styleId="foo" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <r>
                <rPr>
                  <rStyle val="foo"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p>aaa</p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_character_style_referenced_by_paragraph_is_ignored(self):
        style = '''
            <style styleId="foo" type="character">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p>aaa</p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_run_paragraph_mark_style_is_not_used_as_run_style(self):
        style = '''
            <style styleId="foo" type="paragraph">
              <pPr>
                <rPr>
                  <b val="on"/>
                </rPr>
              </pPr>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="foo"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p>aaa</p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )
