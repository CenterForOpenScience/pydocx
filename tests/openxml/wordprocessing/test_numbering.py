# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import (
    AbstractNum,
    Numbering,
    NumberingInstance,
)
from pydocx.util.xml import parse_xml_from_string


class NumberingBaseTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Numbering.load(root)


class NumberingTestCase(NumberingBaseTestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Numbering.load(root)

    def test_numbering_elements_includes_abstractNum_and_num_ordered(self):
        xml = '''
            <numbering>
                <abstractNum abstractNumId="1">
                    <name val="foo"/>
                </abstractNum>
                <num numId="1">
                    <abstractNumId val="1" />
                </num>
            </numbering>
        '''
        numbering = self._load_from_xml(xml)
        expected_classes = [
            AbstractNum,
            NumberingInstance,
        ]
        for obj, expected_class in zip(numbering.elements, expected_classes):
            assert isinstance(obj, expected_class), obj


class NumberingGetNumberingDefinitionTestCase(NumberingBaseTestCase):
    def test_returns_None_with_invalid_num_id(self):
        xml = '''
            <numbering>
                <abstractNum abstractNumId="1">
                    <name val="foo"/>
                </abstractNum>
            </numbering>
        '''
        numbering = self._load_from_xml(xml)
        self.assertEqual(numbering.get_numbering_definition('1'), None)

    def test_returns_None_when_abstract_num_does_not_exist(self):
        xml = '''
            <numbering>
                <abstractNum abstractNumId="2">
                    <name val="foo"/>
                </abstractNum>
                <num numId="1">
                    <abstractNumId val="1" />
                </num>
            </numbering>
        '''
        numbering = self._load_from_xml(xml)
        self.assertEqual(numbering.get_numbering_definition('1'), None)

    def test_returns_numbering_definition_with_valid_num_id(self):
        xml = '''
            <numbering>
                <abstractNum abstractNumId="1">
                    <name val="foo"/>
                </abstractNum>
                <num numId="1">
                    <abstractNumId val="1" />
                </num>
            </numbering>
        '''
        numbering = self._load_from_xml(xml)
        num_definition = numbering.get_numbering_definition('1')
        assert isinstance(num_definition, AbstractNum)
        self.assertEqual(num_definition.name, 'foo')
