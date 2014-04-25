from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase
from xml.etree import cElementTree

from pydocx.exceptions import MalformedDocxException
from pydocx.utils import (
    el_iter,
    find_all,
    find_first,
    remove_namespaces,
    xml_tag_split,
)


def elements_to_tags(elements):
    for element in elements:
        yield element.tag


def make_xml(s):
    xml = b'<?xml version="1.0"?>' + s
    return cElementTree.fromstring(xml)


def remove_whitespace(s):
    return ''.join(s.split())


class UtilsTestCase(TestCase):
    def test_el_iter(self):
        root = make_xml(b'<one><two><three/><three/></two></one>')

        expected = ['one', 'two', 'three', 'three']
        result = el_iter(root)

        self.assertEqual(list(elements_to_tags(result)), expected)

    def test_find_first(self):
        root = make_xml(b'<one><two><three v="1"/><three v="2"/></two></one>')

        # Can't find the root element
        result = find_first(root, 'one')
        self.assertEqual(result, None)

        result = find_first(root, 'three')
        self.assertEqual(result.tag, 'three')
        self.assertEqual(result.get('v'), '1')

        result = find_first(root, 'two')
        self.assertEqual(result.tag, 'two')

    def test_find_all(self):
        root = make_xml(b'<one><two><three/><three/></two></one>')

        # Can't find the root element
        result = find_all(root, 'one')
        self.assertEqual(result, [])

        result = find_all(root, 'three')
        expected = ['three', 'three']
        self.assertEqual(list(elements_to_tags(result)), expected)

        result = find_all(root, 'two')
        self.assertEqual(list(elements_to_tags(result)), ['two'])

    def test_remove_namespaces(self):
        xml = b'''<?xml version="1.0"?>
            <w:one xmlns:w="foo">
                <w:two>
                    <w:three/>
                    <w:three/>
                </w:two>
            </w:one>
        '''
        expected = '<one><two><three/><three/></two></one>'
        result = remove_namespaces(xml)
        assert isinstance(result, bytes)
        result = remove_whitespace(result.decode('utf-8'))
        self.assertEqual(result, expected)

    def test_remove_namespaces_junk_xml_causes_malformed_exception(self):
        self.assertRaises(
            MalformedDocxException,
            lambda: remove_namespaces('foo')
        )

    def test_xml_tag_split(self):
        self.assertEqual(xml_tag_split('{foo}bar'), ('foo', 'bar'))
        self.assertEqual(xml_tag_split('bar'), (None, 'bar'))
