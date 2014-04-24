from __future__ import absolute_import

from unittest import TestCase
from xml.etree import cElementTree

from pydocx.utils import el_iter, find_all, find_first


def elements_to_tags(elements):
    for element in elements:
        yield element.tag


def make_xml(s):
    xml = b'<?xml version="1.0"?>' + s
    return cElementTree.fromstring(xml)


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
