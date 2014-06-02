from pydocx.tests import DocumentGeneratorTestCase


class PropertyHierarchyTestCase(DocumentGeneratorTestCase):
    def test_local_run(self):
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
        expected_html = '''
        <p><strong>aaa</strong></p>
        '''
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
        expected_html = '''
        <p><strong>aaa</strong></p>
        '''
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
        expected_html = '''
        <p><strong>aaa</strong></p>
        '''
        self.assert_xml_body_matches_expected_html(
            xml_body,
            expected_html,
            style=style,
        )
