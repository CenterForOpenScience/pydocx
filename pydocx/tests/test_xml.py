from pydocx.tests.document_builder import DocxBuilder as DXB
from pydocx.tests import _TranslationTestCase


class BoldTestCase(_TranslationTestCase):
    expected_output = """
        <html><body>
            <p><b>AAA</b></p>
            <p>BBB</p>
        </body></html>
    """

    def get_xml(self):
        tags = [
            DXB.p_tag(text='AAA', bold=True),
            DXB.p_tag(text='BBB', bold=True, val='false'),
        ]

        body = ''
        for tag in tags:
            body += tag
        xml = DXB.xml(body)
        return xml
