import os
import time
from itertools import chain

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


class HyperlinkWithBreakTestCase(_TranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = '''
    <html><body>
        <p><a href="www.google.com">link<br/></a></p>
    </body></html>
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link'))
        run_tags.append(DXB.r_tag(None, include_linebreak=True))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
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
        els.extend(tree.find_all('drawing'))
        els.extend(tree.find_all('pict'))
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
        els.extend(tree.find_all('drawing'))
        els.extend(tree.find_all('pict'))
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


class TableTag(_TranslationTestCase):
    expected_output = '''
        <html><body>
            <table>
                <tr>
                    <td>AAA</td>
                    <td>BBB</td>
                </tr>
                <tr>
                    <td>CCC</td>
                    <td>DDD</td>
                </tr>
            </table>
        </body></html>
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('AAA')],
            [DXB.p_tag('BBB')],
            [DXB.p_tag('CCC')],
            [DXB.p_tag('DDD')],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class NestedTableTag(_TranslationTestCase):
    expected_output = '''
    <html><body>
        <table>
            <tr>
                <td>AAA</td>
                <td>BBB</td>
            </tr>
            <tr>
                <td>CCC</td>
                <td>
                    <table>
                        <tr>
                            <td>DDD</td>
                            <td>EEE</td>
                        </tr>
                        <tr>
                            <td>FFF</td>
                            <td>GGG</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body></html>
    '''

    def get_xml(self):
        nested_table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('DDD')],
            [DXB.p_tag('EEE')],
            [DXB.p_tag('FFF')],
            [DXB.p_tag('GGG')],
        ))
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('AAA')],
            [DXB.p_tag('BBB')],
            [DXB.p_tag('CCC')],
            [nested_table],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class TableWithInvalidTag(_TranslationTestCase):
    expected_output = '''
        <html><body>
            <table>
                <tr>
                    <td>AAA</td>
                    <td>BBB</td>
                </tr>
                <tr>
                    <td></td>
                    <td>DDD</td>
                </tr>
            </table>
        </body></html>
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('AAA')],
            [DXB.p_tag('BBB')],
            # This tag may have CCC in it, however this tag has no meaning
            # pertaining to content.
            ['<w:invalidTag>CCC</w:invalidTag>'],
            [DXB.p_tag('DDD')],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class TableWithListAndParagraph(_TranslationTestCase):
    expected_output = '''
    <html><body>
        <table>
            <tr>
                <td>
                    <ol data-list-type="decimal">
                        <li>AAA</li>
                        <li>BBB</li>
                    </ol>
                    CCC<br/>
                    DDD
                </td>
            </tr>
        </table>
    </body></html>
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)
        els = [
            lis,
            DXB.p_tag('CCC'),
            DXB.p_tag('DDD'),
        ]
        td = ''
        for el in els:
            td += el
        table = DXB.table(num_rows=1, num_columns=1, text=chain(
            [td],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class SimpleListTestCase(_TranslationTestCase):
    expected_output = '''
        <html><body>
            <ol data-list-type="lower-alpha">
                <li>AAA</li>
                <li>BBB</li>
                <li>CCC</li>
            </ol>
        </body></html>
    '''

    # Ensure its not failing somewhere and falling back to decimal
    numbering_dict = {
        '1': {
            '0': 'lowerLetter',
        }
    }

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', 0, 1),
            ('CCC', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class SingleListItemTestCase(_TranslationTestCase):
    expected_output = '''
        <html><body>
            <ol data-list-type="lower-alpha">
                <li>AAA</li>
            </ol>
        </body></html>
    '''

    # Ensure its not failing somewhere and falling back to decimal
    numbering_dict = {
        '1': {
            '0': 'lowerLetter',
        }
    }

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class ListWithContinuationTestCase(_TranslationTestCase):
    expected_output = '''
        <html><body>
            <ol data-list-type="decimal">
                <li>AAA<br/>BBB</li>
                <li>CCC
                    <table>
                        <tr>
                            <td>DDD</td>
                            <td>EEE</td>
                        </tr>
                        <tr>
                            <td>FFF</td>
                            <td>GGG</td>
                        </tr>
                    </table>
                </li>
                <li>HHH</li>
            </ol>
        </body></html>
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('DDD')],
            [DXB.p_tag('EEE')],
            [DXB.p_tag('FFF')],
            [DXB.p_tag('GGG')],
        ))
        tags = [
            DXB.li(text='AAA', ilvl=0, numId=1),
            DXB.p_tag('BBB'),
            DXB.li(text='CCC', ilvl=0, numId=1),
            table,
            DXB.li(text='HHH', ilvl=0, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml


class ListWithMultipleContinuationTestCase(_TranslationTestCase):
    expected_output = '''
        <html><body>
            <ol data-list-type="decimal">
                <li>AAA
                    <table>
                        <tr>
                            <td>BBB</td>
                        </tr>
                    </table>
                    <table>
                        <tr>
                            <td>CCC</td>
                        </tr>
                    </table>
                </li>
                <li>DDD</li>
            </ol>
        </body></html>
    '''

    def get_xml(self):
        table1 = DXB.table(num_rows=1, num_columns=1, text=chain(
            [DXB.p_tag('BBB')],
        ))
        table2 = DXB.table(num_rows=1, num_columns=1, text=chain(
            [DXB.p_tag('CCC')],
        ))
        tags = [
            DXB.li(text='AAA', ilvl=0, numId=1),
            table1,
            table2,
            DXB.li(text='DDD', ilvl=0, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml


class MangledIlvlTestCase(_TranslationTestCase):
    expected_output = '''
    <html><body>
        <ol data-list-type="decimal">
            <li>AAA</li>
        </ol>
        <ol data-list-type="decimal">
            <li>BBB
                <ol data-list-type="decimal">
                    <li>CCC</li>
                </ol>
            </li>
        </ol>
    </body></html>
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 2),
            ('BBB', 1, 1),
            ('CCC', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class SeperateListsTestCase(_TranslationTestCase):
    expected_output = '''
    <html><body>
        <ol data-list-type="decimal">
            <li>AAA</li>
        </ol>
        <ol data-list-type="decimal">
            <li>BBB</li>
        </ol>
        <ol data-list-type="decimal">
            <li>CCC</li>
        </ol>
    </body></html>
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 2),
            # Because AAA and CCC are part of the same list (same list id)
            # and BBB is different, these need to be split into three
            # lists (or lose everything from BBB and after.
            ('BBB', 0, 1),
            ('CCC', 0, 2),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class InvalidIlvlOrderTestCase(_TranslationTestCase):
    expected_output = '''
    <html><body>
        <ol data-list-type="decimal">
            <li>AAA
                <ol data-list-type="decimal">
                    <li>BBB
                        <ol data-list-type="decimal">
                            <li>CCC</li>
                        </ol>
                    </li>
                </ol>
            </li>
        </ol>
    </body></html>
    '''

    def get_xml(self):
        tags = [
            DXB.li(text='AAA', ilvl=1, numId=1),
            DXB.li(text='BBB', ilvl=3, numId=1),
            DXB.li(text='CCC', ilvl=2, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml


class DeeplyNestedTableTestCase(_TranslationTestCase):
    expected_output = '''
    '''
    run_expected_output = False

    def get_xml(self):
        table = DXB.p_tag('AAA')

        for _ in range(50):
            table = DXB.table(num_rows=1, num_columns=1, text=chain(
                [table],
            ))
        body = table
        xml = DXB.xml(body)
        return xml

    def test_performance(self):
        if not os.environ.get('TRAVIS_EXECUTE_PERFORMANCE', False):
            raise SkipTest('TRAVIS_EXECUTE_PERFORMANCE is false')
        with self.toggle_run_expected_output():
            start_time = time.time()
            try:
                self.test_expected_output()
            except AssertionError:
                pass
            end_time = time.time()
            total_time = end_time - start_time
            # This finishes in under a second on python 2.7
            assert total_time < 5, total_time


class NonStandardTextTagsTestCase(_TranslationTestCase):
    expected_output = '''
    <html><body>
        <p><span class='insert' author='' date=''>insert </span>
        smarttag</p>
    </body></html>
    '''

    def get_xml(self):
        run_tags = [DXB.r_tag(i) for i in 'insert ']
        insert_tag = DXB.insert_tag(run_tags)
        run_tags = [DXB.r_tag(i) for i in 'smarttag']
        smart_tag = DXB.smart_tag(run_tags)

        run_tags = [insert_tag, smart_tag]
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class RTagWithNoText(_TranslationTestCase):
    expected_output = '<html><body></body></html>'

    def get_xml(self):
        p_tag = DXB.p_tag(None)  # No text
        run_tags = [p_tag]
        # The bug is only present in a hyperlink
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        body = DXB.p_tag(run_tags)

        xml = DXB.xml(body)
        return xml
