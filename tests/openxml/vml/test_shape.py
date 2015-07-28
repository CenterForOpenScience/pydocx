# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.vml import Shape
from pydocx.util.xml import parse_xml_from_string


class ShapeGetStyleTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Shape.load(root)

    def test_empty_style_spec(self):
        xml = '''
          <shape style="" />
        '''
        shape = self._load_from_xml(xml)
        style = shape.get_style()
        expected_style = {}
        self.assertEqual(style, expected_style)

    def test_single_item_style_spec(self):
        xml = '''
          <shape id="_x0000_s1028" type="#_x0000_t75" style="width:484pt"/>
        '''
        shape = self._load_from_xml(xml)
        style = shape.get_style()
        expected_style = dict(
            width='484pt',
        )
        self.assertEqual(style, expected_style)

    def test_multi_item_style_spec(self):
        xml = '''
          <shape style="width:484pt;height:126pt"/>
        '''
        shape = self._load_from_xml(xml)
        style = shape.get_style()
        expected_style = dict(
            width='484pt',
            height='126pt',
        )
        self.assertEqual(style, expected_style)

    def test_multi_item_style_spec_with_trailing_comma(self):
        xml = '''
          <shape style="width:484pt;height:126pt;"/>
        '''
        shape = self._load_from_xml(xml)
        style = shape.get_style()
        expected_style = dict(
            width='484pt',
            height='126pt',
        )
        self.assertEqual(style, expected_style)

    def test_malformed_style_spec(self):
        xml = '''
          <shape style="width:484pt:foo;height:126pt"/>
        '''
        shape = self._load_from_xml(xml)
        style = shape.get_style()
        expected_style = dict(
            width='484pt:foo',
            height='126pt',
        )
        self.assertEqual(style, expected_style)
