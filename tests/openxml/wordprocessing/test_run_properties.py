# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import RunProperties
from pydocx.util.xml import parse_xml_from_string


class RunPropertiesTestCase(TestCase):
    def _load_styles_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return RunProperties.load(root)

    def test_bold_on(self):
        xml = b'''
            <rPr>
              <b val='on' />
            </rPr>
        '''
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.bold.value, 'on')
        assert bool(properties.bold)

    def test_bold_off(self):
        xml = b'''
            <rPr>
              <b val='off' />
            </rPr>
        '''
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.bold.value, 'off')
        assert not bool(properties.bold)

    def test_items(self):
        xml = b'''
            <rPr>
              <b val='off' />
              <i val='on' />
            </rPr>
        '''
        properties = self._load_styles_from_xml(xml)
        result = dict(properties.items())
        self.assertEqual(
            sorted(result.keys()),
            sorted(['bold', 'italic']),
        )
        assert not bool(result['bold'])
        assert bool(result['italic'])
