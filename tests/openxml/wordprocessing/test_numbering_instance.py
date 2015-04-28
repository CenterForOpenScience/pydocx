# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import LevelOverride, NumberingInstance
from pydocx.util.xml import parse_xml_from_string


class NumberingInstanceTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return NumberingInstance.load(root)

    def test_numId_mapped_to_num_id_attribute(self):
        xml = b'''
            <num numId="100">
            </num>
        '''
        num = self._load_from_xml(xml)
        self.assertEqual(num.num_id, "100")

    def test_abstractNumId_child_mapped_to_abstract_num_id(self):
        xml = b'''
            <num numId="100">
                <abstractNumId val="200" />
            </num>
        '''
        num = self._load_from_xml(xml)
        self.assertEqual(num.abstract_num_id, "200")

    def test_lvlOverride_collection_mapped_to_level_overrides(self):
        xml = b'''
            <num numId="100">
                <startOverride val="200" />
                <lvlOverride ilvl="1" />
                <lvlOverride ilvl="2" />
                <lvlOverride ilvl="3" />
            </num>
        '''
        num = self._load_from_xml(xml)
        expected_classes = [
            (LevelOverride, "1"),
            (LevelOverride, "2"),
            (LevelOverride, "3"),
        ]
        for obj, (expected_class, level_id) in zip(
            num.level_overrides,
            expected_classes,
        ):
            assert isinstance(obj, expected_class), obj
            self.assertEqual(obj.level_id, level_id)
