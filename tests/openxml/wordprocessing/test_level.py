# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import (
    Level,
    ParagraphProperties,
    RunProperties,
)
from pydocx.util.xml import parse_xml_from_string


class LevelTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Level.load(root)

    def test_ilvl_mapped_to_level_id_attribute(self):
        xml = b'''
            <lvl ilvl="100">
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.level_id, "100")

    def test_starting_position_attribute(self):
        xml = b'''
            <lvl>
                <start val="50" />
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.start, "50")

    def test_num_format_attribute(self):
        xml = b'''
            <lvl>
                <numFmt val="decimal" />
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.num_format, "decimal")

    def test_restart_attribute(self):
        xml = b'''
            <lvl>
                <lvlRestart val="1" />
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.restart, "1")

    def test_associated_paragraph_style_attribute(self):
        xml = b'''
            <lvl>
                <pStyle val="normal" />
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.paragraph_style, "normal")

    def test_run_properties_child(self):
        xml = b'''
            <lvl>
                <rPr />
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.run_properties.__class__, RunProperties)

    def test_paragraph_properties_child(self):
        xml = b'''
            <lvl>
                <pPr />
            </lvl>
        '''
        level = self._load_from_xml(xml)
        self.assertEqual(level.paragraph_properties.__class__, ParagraphProperties)  # noqa
