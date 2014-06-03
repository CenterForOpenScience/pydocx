from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase
from xml.etree import cElementTree

from pydocx.styles import Styles


class StylesTestCase(TestCase):
    def _load_styles_from_xml(self, xml):
        root = cElementTree.fromstring(xml)
        return Styles.load(root)

    def test_style_information_is_loaded(self):
        xml = b'''
            <styles>
              <style type="character" styleId="foo">
                <name val="Foo"/>
              </style>
            </styles>
        '''
        styles = self._load_styles_from_xml(xml)
        self.assertEqual(len(styles.styles), 1)
        style = styles.styles[0]
        self.assertEqual(style.style_type, 'character')
        self.assertEqual(style.style_id, 'foo')
        self.assertEqual(style.name, 'Foo')

    def test_multiple_styles(self):
        xml = b'''
            <styles>
              <style styleId="foo">
              </style>
              <style styleId="bar">
              </style>
            </styles>
        '''
        styles = self._load_styles_from_xml(xml)
        self.assertEqual(len(styles.styles), 2)
        self.assertEqual(styles.styles[0].style_id, 'foo')
        self.assertEqual(styles.styles[1].style_id, 'bar')

    def test_default_type_is_paragraph(self):
        xml = b'''
            <styles>
              <style styleId="foo">
              </style>
            </styles>
        '''
        styles = self._load_styles_from_xml(xml)
        self.assertEqual(styles.styles[0].style_type, 'paragraph')
