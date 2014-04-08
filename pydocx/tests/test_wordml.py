from __future__ import absolute_import

import unittest
from xml.etree import cElementTree

from pydocx.packaging import ZipPackage
from pydocx.utils import (
    xml_tag_split,
)
from pydocx.wordml import MainDocumentPart, WordprocessingDocument
from pydocx.xml import XmlNamespaceManager


class ZipPackageTestCase(unittest.TestCase):
    def setUp(self):
        self.package = ZipPackage(
            path='pydocx/fixtures/no_break_hyphen.docx',
        )

    def test_relationship_uri(self):
        self.assertEqual(
            self.package.relationship_uri,
            '/_rels/.rels',
        )

    def test_relationship_part_exists(self):
        assert self.package.part_exists(self.package.relationship_uri)

    def test_word_document_part_exists(self):
        assert self.package.part_exists('/word/document.xml')

    def test_package_relationship_part_stream(self):
        part = self.package.get_part('/_rels/.rels')
        data = part.stream.read()
        assert data
        assert data.startswith('<?xml version="1.0" encoding="UTF-8"?>')


class WordprocessingDocumentTestCase(unittest.TestCase):
    def setUp(self):
        self.document = WordprocessingDocument(
            path='pydocx/fixtures/no_break_hyphen.docx',
        )

    def test_document_is_the_open_xml_package(self):
        self.assertEqual(
            self.document,
            self.document.main_document_part.open_xml_package,
        )

    def test_get_parts_of_type_office_document(self):
        self.assertEqual(
            self.document.get_parts_of_type(
                MainDocumentPart.relationship_type,
            )[0],
            self.document.main_document_part,
        )

    def test_main_document_part_uri(self):
        self.assertEqual(
            self.document.main_document_part.uri,
            '/word/document.xml',
        )

    def test_main_document_part_root(self):
        namespace, tag = xml_tag_split(
            self.document.main_document_part.root_element.tag,
        )
        self.assertEqual(tag, 'document')


class XmlNamespaceManagerTestCase(unittest.TestCase):
    def test_namespace_manager(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <a:foo
                xmlns:a="http://example/test" xmlns:b="http://example2/test2">
                <a:cat />
                <b:dog />
                <a:mouse><a:bat /></a:mouse>
            </a:foo>
        '''
        root = cElementTree.fromstring(xml)
        manager = XmlNamespaceManager()
        manager.add_namespace('http://example/test')
        tags = []
        for element in manager.select(root):
            tags.append(element.tag)
        expected_tags = [
            '{http://example/test}cat',
            '{http://example/test}mouse',
        ]
        self.assertEqual(tags, expected_tags)

        manager.add_namespace('http://example2/test2')
        tags = []
        for element in manager.select(root):
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
        for element in manager.select(root):
            tags.append(element.tag)
        expected_tags = [
            '{http://example2/test2}dog',
        ]
        self.assertEqual(tags, expected_tags)
