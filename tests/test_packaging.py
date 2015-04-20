# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import unittest

from pydocx.packaging import ZipPackage


class ZipPackageTestCase(unittest.TestCase):
    def setUp(self):
        self.package = ZipPackage(
            path='tests/fixtures/no_break_hyphen.docx',
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
        assert data.startswith(b'<?xml version="1.0" encoding="UTF-8"?>')
