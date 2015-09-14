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
        result = dict(properties.fields)
        self.assertEqual(
            sorted(result.keys()),
            sorted(['bold', 'italic']),
        )
        assert not bool(result['bold'])
        assert bool(result['italic'])

    def test_size_property_returns_None_when_sz_is_None(self):
        xml = '<rPr />'
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.size, None)

    def test_size_property_returns_int_of_sz(self):
        xml = '<rPr><sz val="10"/></rPr>'
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.size, int(properties.sz))

    def test_position_property_returns_0_when_pos_is_None(self):
        xml = '<rPr />'
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.position, 0)

    def test_position_property_returns_int_of_position(self):
        xml = '<rPr><position val="10"/></rPr>'
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.position, int(properties.pos))

    def test_size_property_can_be_a_decimal(self):
        xml = '<rPr><sz val="10.1234"/></rPr>'
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.size, 10.1234)

    def test_size_property_has_garbage_returns_0(self):
        xml = '<rPr><sz val="abcdef"/></rPr>'
        properties = self._load_styles_from_xml(xml)
        self.assertEqual(properties.size, None)
