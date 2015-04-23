# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Style
from pydocx.util.xml import parse_xml_from_string


class StyleTestCase(TestCase):
    def _load_styles_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Style.load(root)

    def test_style_information_is_loaded(self):
        xml = b'''
            <style type="character" styleId="foo">
              <name val="Foo"/>
            </style>
        '''
        style = self._load_styles_from_xml(xml)
        self.assertEqual(style.style_type, 'character')
        self.assertEqual(style.style_id, 'foo')
        self.assertEqual(style.name, 'Foo')

    def test_default_type_is_paragraph(self):
        xml = b'''
            <style styleId="foo">
            </style>
        '''
        style = self._load_styles_from_xml(xml)
        self.assertEqual(style.style_type, 'paragraph')

    def test_run_properties_are_loaded(self):
        xml = b'''
            <style styleId="foo">
              <rPr>
                <b val="on" />
              </rPr>
            </style>
        '''
        style = self._load_styles_from_xml(xml)
        self.assertEqual(style.run_properties.bold.value, 'on')
        assert bool(style.run_properties.bold)

    def test_basedOn_sets_parent_style_attribute(self):
        xml = b'''
            <style styleId="foo">
              <basedOn val="bar" />
            </style>
        '''
        style = self._load_styles_from_xml(xml)
        self.assertEqual(style.parent_style, 'bar')
