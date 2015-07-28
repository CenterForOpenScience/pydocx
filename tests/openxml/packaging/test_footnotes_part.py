# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import unittest

from pydocx.openxml.packaging import (
    MainDocumentPart,
    FootnotesPart,
    WordprocessingDocument,
)
from pydocx.openxml.wordprocessing import Footnotes
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.util.zip import create_zip_archive


class FootnotesPartTestCase(unittest.TestCase):
    def test_footnotes_property_is_a_Footnotes_instance(self):
        factory = WordprocessingDocumentFactory()
        factory.add(FootnotesPart, '')
        factory.add(MainDocumentPart, '')

        package = create_zip_archive(factory.to_zip_dict())
        # TODO the interface for creating a new WordprocessingDocument sucks
        document = WordprocessingDocument(path=package)
        part = document.main_document_part.footnotes_part
        assert isinstance(part.footnotes, Footnotes), part.footnotes
