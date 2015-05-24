# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Body
from pydocx.util.xml import parse_xml_from_string


class BodyTestCase(TestCase):
    def _load_from_xml(self, xml):
        root = parse_xml_from_string(xml)
        return Body.load(root)

    def test_next_child_that_does_not_exist(self):
        xml = b'''
            <body />
        '''
        body = self._load_from_xml(xml)
        child = body.next_child(123)
        self.assertEqual(child, None)

    def test_previous_child_that_does_not_exist(self):
        xml = b'''
            <body />
        '''
        body = self._load_from_xml(xml)
        child = body.previous_child(123)
        self.assertEqual(child, None)

    def test_next_child(self):
        xml = b'''
            <body>
                <p />
                <p />
            </body>
        '''
        body = self._load_from_xml(xml)
        child = body.next_child(body.children[0])
        self.assertEqual(child, body.children[1])

    def test_next_child_for_last_child(self):
        xml = b'''
            <body>
                <p />
                <p />
            </body>
        '''
        body = self._load_from_xml(xml)
        child = body.next_child(body.children[-1])
        self.assertEqual(child, None)

    def test_previous_child_for_first_child(self):
        xml = b'''
            <body>
                <p />
                <p />
            </body>
        '''
        body = self._load_from_xml(xml)
        child = body.previous_child(body.children[0])
        self.assertEqual(child, None)

    def test_previous_child(self):
        xml = b'''
            <body>
                <p />
                <p />
            </body>
        '''
        body = self._load_from_xml(xml)
        child = body.previous_child(body.children[1])
        self.assertEqual(child, body.children[0])
