# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Level, LevelOverride
from pydocx.util.xml import parse_xml_from_string


class LevelOverrideTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return LevelOverride.load(root)

    def test_ilvl_mapped_to_level_id_attribute(self):
        xml = b'''
            <lvlOverride ilvl="100">
            </lvlOverride>
        '''
        override = self._load_from_xml(xml)
        self.assertEqual(override.level_id, "100")

    def test_startOverride_child_mapped_to_start_override_attribute(self):
        xml = b'''
            <lvlOverride ilvl="100">
                <startOverride val="200" />
            </lvlOverride>
        '''
        override = self._load_from_xml(xml)
        self.assertEqual(override.start_override, "200")

    def test_level_child_mapped_to_level_class(self):
        xml = b'''
            <lvlOverride ilvl="100">
                <startOverride val="200" />
                <lvl />
            </lvlOverride>
        '''
        override = self._load_from_xml(xml)
        assert isinstance(override.level, Level), override.level
