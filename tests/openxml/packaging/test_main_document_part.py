# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import unittest

from pydocx.openxml.packaging import (
    MainDocumentPart,
    WordprocessingDocument,
)
from pydocx.openxml.wordprocessing import Document
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.util.zip import create_zip_archive


class MainDocumentPartTestCase(unittest.TestCase):
    def test_document_property_is_a_Document_instance(self):
        factory = WordprocessingDocumentFactory()
        factory.add(MainDocumentPart, '')

        package = create_zip_archive(factory.to_zip_dict())
        # TODO the interface for creating a new WordprocessingDocument sucks
        document = WordprocessingDocument(path=package)
        part = document.main_document_part
        assert isinstance(part.document, Document), part.document
