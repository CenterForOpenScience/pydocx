# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Styles
from pydocx.util.xml import parse_xml_from_string


class StylesTestCase(TestCase):
    def _load_styles_from_xml(self, xml):
        root = parse_xml_from_string(xml)
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

    def test_get_styles_by_type(self):
        xml = b'''
            <styles>
              <style styleId="foo">
                <name val="One"/>
              </style>
              <style styleId="bar" type="paragraph">
                <name val="Two"/>
              </style>
              <style styleId="baz" type="character">
                <name val="Three"/>
              </style>
            </styles>
        '''
        styles = self._load_styles_from_xml(xml)
        paragraph_styles = styles.get_styles_by_type('paragraph')
        self.assertEqual(paragraph_styles['foo'].name, 'One')
        self.assertEqual(paragraph_styles['bar'].name, 'Two')
        self.assertRaises(KeyError, lambda: paragraph_styles['baz'])

        character_styles = styles.get_styles_by_type('character')
        self.assertEqual(character_styles['baz'].name, 'Three')
        self.assertRaises(KeyError, lambda: character_styles['foo'])
        self.assertRaises(KeyError, lambda: character_styles['bar'])
