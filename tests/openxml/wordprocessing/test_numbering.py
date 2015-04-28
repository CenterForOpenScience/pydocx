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


class NumberingTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Numbering.load(root)

    def test_numbering_elements_includes_abstractNum_and_num_ordered(self):
        xml = b'''
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
