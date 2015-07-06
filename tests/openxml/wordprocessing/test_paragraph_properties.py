# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import NumberingProperties, ParagraphProperties  # noqa
from pydocx.util.xml import parse_xml_from_string


class ParagraphPropertiesTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return ParagraphProperties.load(root)

    def test_pStyle_child_mapped_to_parent_style_attribute(self):
        xml = '''
            <pPr>
                <pStyle val="foostyle" />
            </pPr>
        '''
        properties = self._load_from_xml(xml)
        self.assertEqual(properties.parent_style, "foostyle")

    def test_numPr_child_mapped_to_numbering_properties_attribute(self):
        xml = '''
            <pPr>
                <numPr />
            </pPr>
        '''
        properties = self._load_from_xml(xml)
        assert isinstance(properties.numbering_properties, NumberingProperties)

    def test_indentation_left(self):
        xml = '''
            <pPr>
                <ind left="123" right="456" firstLine="789" />
            </pPr>
        '''
        properties = self._load_from_xml(xml)
        self.assertEqual(properties.indentation_left, '123')

    def test_indentation_right(self):
        xml = '''
            <pPr>
                <ind left="123" right="456" firstLine="789" />
            </pPr>
        '''
        properties = self._load_from_xml(xml)
        self.assertEqual(properties.indentation_right, '456')

    def test_indentation_first_line(self):
        xml = '''
            <pPr>
                <ind left="123" right="456" firstLine="789" />
            </pPr>
        '''
        properties = self._load_from_xml(xml)
        self.assertEqual(properties.indentation_first_line, '789')
