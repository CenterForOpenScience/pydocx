# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import unittest

from pydocx.openxml.packaging import (
    MainDocumentPart,
    NumberingDefinitionsPart,
    WordprocessingDocument,
)
from pydocx.openxml.wordprocessing import Numbering
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.util.zip import create_zip_archive


class NumberingDefinitionsPartTestCase(unittest.TestCase):
    def test_numbering_property_is_a_Numbering_instance(self):
        factory = WordprocessingDocumentFactory()
        factory.add(NumberingDefinitionsPart, '')
        factory.add(MainDocumentPart, '')

        package = create_zip_archive(factory.to_zip_dict())
        # TODO the interface for creating a new WordprocessingDocument sucks
        document = WordprocessingDocument(path=package)
        part = document.main_document_part.numbering_definitions_part
        assert isinstance(part.numbering, Numbering), part.numbering
