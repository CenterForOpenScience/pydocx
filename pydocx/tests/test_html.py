from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.tests import DocumentGeneratorTestCase


class ParagraphTestCase(DocumentGeneratorTestCase):
    def test_multiple_text_tags_in_a_single_run_tag(self):
        xml_body = '''
            <p>
              <r>
                <t>A</t>
                <t>B</t>
                <t>C</t>
              </r>
            </p>
        '''
        expected_html = '<p>ABC</p>'
        self.assert_xml_body_matches_expected_html(xml_body, expected_html)

    def test_empty_text_tag(self):
        xml_body = '''
            <p>
              <r>
                <t></t>
              </r>
            </p>
        '''
        expected_html = ''
        self.assert_xml_body_matches_expected_html(xml_body, expected_html)


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
        style_template = '''
            <style styleId="heading%s" type="paragraph">
              <name val="Heading %s"/>
            </style>
        '''

        style = ''.join(
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

        xml_body = ''.join(
            paragraph_template % entry
            for entry in style_to_text
        )

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


class StyleBasedOnTestCase(DocumentGeneratorTestCase):
    def test_loop_detection(self):
        style = '''
            <style styleId="one">
              <basedOn val="three"/>
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
            <style styleId="two">
              <basedOn val="one"/>
            </style>
            <style styleId="three">
              <basedOn val="two"/>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="three"/>
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

    def test_styles_are_inherited(self):
        style = '''
            <style styleId="one">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
            <style styleId="two">
              <basedOn val="one"/>
              <rPr>
                <i val="on"/>
              </rPr>
            </style>
            <style styleId="three">
              <basedOn val="two"/>
              <rPr>
                <u val="single"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="three"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '''
            <p>
              <span class="pydocx-underline">
                <em>
                  <strong>aaa</strong>
                </em>
              </span>
            </p>
        '''
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_character_style_may_only_be_based_on_character_style(self):
        # character styles may only be based on other character styles
        # otherwise, the based on specification should be ignored
        style = '''
            <style styleId="one" type="paragraph">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
            <style styleId="two" type="character">
              <basedOn val="one"/>
              <rPr>
                <i val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <r>
                <rPr>
                  <rStyle val="two"/>
                </rPr>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p><em>aaa</em></p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )

    def test_paragraph_style_may_only_be_based_on_paragraph_style(self):
        # paragraph styles may only be based on other paragraph styles
        # otherwise, the based on specification should be ignored
        style = '''
            <style styleId="one" type="character">
              <rPr>
                <b val="on"/>
              </rPr>
            </style>
            <style styleId="two" type="paragraph">
              <basedOn val="one"/>
              <rPr>
                <i val="on"/>
              </rPr>
            </style>
        '''

        xml_body = '''
            <p>
              <pPr>
                <pStyle val="two"/>
              </pPr>
              <r>
                <t>aaa</t>
              </r>
            </p>
        '''
        expected_html = '<p><em>aaa</em></p>'
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )
