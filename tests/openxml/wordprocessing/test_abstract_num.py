# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import AbstractNum, Level
from pydocx.util.xml import parse_xml_from_string


class AbstractNumTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return AbstractNum.load(root)

    def test_abstractNumId_mapped_to_abstract_num_id(self):
        xml = b'''
            <abstractNum abstractNumId="100">
            </abstractNum>
        '''
        num = self._load_from_xml(xml)
        self.assertEqual(num.abstract_num_id, "100")

    def test_name_child_mapped_to_name(self):
        xml = b'''
            <abstractNum abstractNumId="100">
                <name val="foo" />
            </abstractNum>
        '''
        num = self._load_from_xml(xml)
        self.assertEqual(num.name, "foo")

    def test_lvl_collection_mapped_to_levels(self):
        xml = b'''
            <abstractNum abstractNumId="100">
                <name val="foo" />
                <lvl ilvl="1" />
                <lvl ilvl="2" />
                <lvl ilvl="3" />
            </abstractNum>
        '''
        num = self._load_from_xml(xml)
        expected_classes = [
            (Level, "1"),
            (Level, "2"),
            (Level, "3"),
        ]
        classes = [
            (element.__class__, element.level_id)
            for element in num.levels
        ]
        self.assertEqual(classes, expected_classes)
