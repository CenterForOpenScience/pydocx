import os
from nose.plugins.skip import SkipTest

from pydocx.tests.document_builder import DocxBuilder as DXB
from pydocx.tests import (
    ElementTree,
    XMLDocx2Html,
    _TranslationTestCase,
    remove_namespaces,
)


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


class ImageTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'media/image1.jpeg',
        'rId1': 'media/image2.jpeg',
    }
    expected_output = '''
        <html><body>
            <p>
                <img src="media/image1.jpeg" height="20px" width="40px" />
            </p>
            <p>
                <img src="media/image2.jpeg" height="21pt" width="41pt" />
            </p>
        </body></html>
    '''

    def get_xml(self):
        drawing = DXB.drawing(height=20, width=40, r_id='rId0')
        pict = DXB.pict(height=21, width=41, r_id='rId1')
        tags = [
            drawing,
            pict,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml

    def test_get_image_id(self):
        parser = XMLDocx2Html(
            document_xml=self.get_xml(),
            rels_dict=self.relationship_dict,
        )
        tree = ElementTree.fromstring(
            remove_namespaces(self.get_xml()),
        )
        els = []
        els.extend(tree.findall_all('drawing'))
        els.extend(tree.findall_all('pict'))
        image_ids = []
        for el in els:
            image_ids.append(parser._get_image_id(el))
        expected = [
            'rId0',
            'rId1',
        ]
        self.assertEqual(
            set(image_ids),
            set(expected),
        )

    def test_get_image_sizes(self):
        parser = XMLDocx2Html(
            document_xml=self.get_xml(),
            rels_dict=self.relationship_dict,
        )
        tree = ElementTree.fromstring(
            remove_namespaces(self.get_xml()),
        )
        els = []
        els.extend(tree.findall_all('drawing'))
        els.extend(tree.findall_all('pict'))
        image_ids = []
        for el in els:
            image_ids.append(parser._get_image_size(el))
        expected = [
            ('40px', '20px'),
            ('41pt', '21pt'),
        ]
        self.assertEqual(
            set(image_ids),
            set(expected),
        )


class ImageNotInRelsDictTestCase(_TranslationTestCase):
    relationship_dict = {
        # 'rId0': 'media/image1.jpeg',
    }
    expected_output = '''
        <html><body>
        </body></html>
    '''

    def get_xml(self):
        drawing = DXB.drawing(height=20, width=40, r_id='rId0')
        body = drawing

        xml = DXB.xml(body)
        return xml


class ImageNoSizeTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'fixtures',
            'bullet_go_gray.png',
        )
    }
    image_sizes = {
        'rId0': (0, 0),
    }
    expected_output = '''
        <html>
            <p>
                <img src="%s" />
            </p>
        </html>
    ''' % relationship_dict['rId0']

    @staticmethod
    def image_handler(image_id, relationship_dict):
        return relationship_dict.get(image_id)

    def get_xml(self):
        raise SkipTest(
            'Since we are not using PIL, we do not need this test yet.',
        )
        drawing = DXB.drawing('rId0')
        tags = [
            drawing,
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml
