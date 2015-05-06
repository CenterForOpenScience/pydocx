# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import NumberingProperties
from pydocx.util.xml import parse_xml_from_string


class NumberingPropertiesBaseTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return NumberingProperties.load(root)


class NumberingPropertiesTestCase(NumberingPropertiesBaseTestCase):
    def test_numId_child_mapped_to_num_id_attribute(self):
        xml = '''
            <numPr>
                <numId val="100"/>
                <ilvl val="200"/>
            </numPr>
        '''
        num = self._load_from_xml(xml)
        self.assertEqual(num.num_id, "100")

    def test_ilvl_child_mapped_to_level_id_attribute(self):
        xml = '''
            <numPr>
                <numId val="100"/>
                <ilvl val="200"/>
            </numPr>
        '''
        num = self._load_from_xml(xml)
        self.assertEqual(num.level_id, "200")


class NumberingPropertiesIsRootLevelTestCase(NumberingPropertiesBaseTestCase):
    def test_false_when_num_id_is_None(self):
        xml = '''
            <numPr>
                <ilvl val="0"/>
            </numPr>
        '''
        num = self._load_from_xml(xml)
        assert not num.is_root_level()

    def test_false_when_level_id_is_None(self):
        xml = '''
            <numPr>
                <numId val="100"/>
            </numPr>
        '''
        num = self._load_from_xml(xml)
        assert not num.is_root_level()

    def test_false_when_both_num_id_and_level_id_are_None(self):
        xml = '''
            <numPr>
            </numPr>
        '''
        num = self._load_from_xml(xml)
        assert not num.is_root_level()

    def test_false_when_level_id_is_not_root(self):
        xml = '''
            <numPr>
                <numId val="100"/>
                <ilvl val="200"/>
            </numPr>
        '''
        num = self._load_from_xml(xml)
        assert not num.is_root_level()

    def test_true_when_level_id_is_root(self):
        xml = '''
            <numPr>
                <numId val="100"/>
                <ilvl val="{root}"/>
            </numPr>
        '''.format(root=NumberingProperties.ROOT_LEVEL_ID)
        num = self._load_from_xml(xml)
        assert num.is_root_level()
