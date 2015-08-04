# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.exceptions import MalformedDocxException
from pydocx.util.xml import (
    el_iter,
    parse_xml_from_string,
    xml_remove_namespaces,
    xml_tag_split,
    XmlNamespaceManager,
)


def elements_to_tags(elements):
    for element in elements:
        yield element.tag


def make_xml(s):
    xml = b'<?xml version="1.0"?>' + s
    return parse_xml_from_string(xml)


def remove_whitespace(s):
    return ''.join(s.split())


class UtilsTestCase(TestCase):
    def test_el_iter(self):
        root = make_xml(b'<one><two><three/><three/></two></one>')

        expected = ['one', 'two', 'three', 'three']
        result = el_iter(root)

        self.assertEqual(list(elements_to_tags(result)), expected)

    def test_remove_namespaces(self):
        xml = b'''<?xml version="1.0"?>
            <w:one xmlns:w="foo">
                <w:two>
                    <w:three/>
                    <w:three/>
                </w:two>
            </w:one>
        '''
        expected = '<one><two><three/><three/></two></one>'
        result = xml_remove_namespaces(xml)
        assert isinstance(result, bytes)
        result = remove_whitespace(result.decode('utf-8'))
        self.assertEqual(result, expected)

    def test_remove_namespaces_on_namespaceless_xml(self):
        xml = b'<?xml version="1.0"?><one><two><three/><three/></two></one>'
        expected = '<one><two><three/><three/></two></one>'
        result = xml_remove_namespaces(xml)
        assert isinstance(result, bytes)
        result = remove_whitespace(result.decode('utf-8'))
        self.assertEqual(result, expected)

    def test_remove_namespaces_junk_xml_causes_malformed_exception(self):
        self.assertRaises(
            MalformedDocxException,
            lambda: xml_remove_namespaces('foo')
        )

    def test_xml_tag_split(self):
        self.assertEqual(xml_tag_split('{foo}bar'), ('foo', 'bar'))
        self.assertEqual(xml_tag_split('bar'), (None, 'bar'))


class XmlNamespaceManagerTestCase(TestCase):
    def test_namespace_manager(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <a:foo
                xmlns:a="http://example/test" xmlns:b="http://example2/test2">
                <a:cat />
                <b:dog />
                <a:mouse><a:bat /></a:mouse>
            </a:foo>
        '''
        root = parse_xml_from_string(xml)
        manager = XmlNamespaceManager()
        manager.add_namespace('http://example/test')
        tags = []
        for element in manager.iterate_children(root):
            tags.append(element.tag)
        expected_tags = [
            '{http://example/test}cat',
            '{http://example/test}mouse',
        ]
        self.assertEqual(tags, expected_tags)

        manager.add_namespace('http://example2/test2')
        tags = []
        for element in manager.iterate_children(root):
            tags.append(element.tag)
        expected_tags = [
            '{http://example/test}cat',
            '{http://example2/test2}dog',
            '{http://example/test}mouse',
        ]
        self.assertEqual(tags, expected_tags)

        manager = XmlNamespaceManager()
        manager.add_namespace('http://example2/test2')
        tags = []
        for element in manager.iterate_children(root):
            tags.append(element.tag)
        expected_tags = [
            '{http://example2/test2}dog',
        ]
        self.assertEqual(tags, expected_tags)
