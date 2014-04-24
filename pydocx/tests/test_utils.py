from __future__ import absolute_import, unicode_literals

from unittest import TestCase
from xml.etree import cElementTree

from pydocx.utils import el_iter


def elements_to_tags(elements):
    for element in elements:
        yield element.tag


class UtilsTestCase(TestCase):
    def test_el_iter(self):
        xml = b'<?xml version="1.0" ?><one><two><three/></two></one>'
        root = cElementTree.fromstring(xml)

        expected = ['one', 'two', 'three']
        result = el_iter(root)

        self.assertEqual(list(elements_to_tags(result)), expected)
