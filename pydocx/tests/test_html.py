from pydocx.tests import DocumentGeneratorTestCase


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
