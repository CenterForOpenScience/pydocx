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


class HyperlinkVanillaTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = '''
    <html><body>
        <p><a href="www.google.com">link</a>.</p>
    </body></html>
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link', is_bold=False))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkWithMultipleRunsTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = '''
    <html><body>
        <p><a href="www.google.com">link</a>.</p>
    </body></html>
    '''

    def get_xml(self):
        run_tags = [DXB.r_tag(i) for i in 'link']
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkNoTextTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = '''
    <html><body>
    </body></html>
    '''

    def get_xml(self):
        run_tags = []
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkNotInRelsDictTestCase(_TranslationTestCase):
    relationship_dict = {
        # 'rId0': 'www.google.com', missing
    }

    expected_output = '''
    <html><body>
        <p>link.</p>
    </body></html>
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link', is_bold=False))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml
