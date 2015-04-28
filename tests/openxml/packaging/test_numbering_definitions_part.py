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
    def test_document_is_the_open_xml_package(self):
        factory = WordprocessingDocumentFactory()
        document_xml = b'<document />'
        numbering_xml = b'<numbering />'
        factory.add(NumberingDefinitionsPart, numbering_xml)
        factory.add(MainDocumentPart, document_xml)

        package = create_zip_archive(factory.to_zip_dict())
        # TODO the interface for creating a new WordprocessingDocument sucks
        document = WordprocessingDocument(path=package)
        part = document.main_document_part.numbering_definitions_part
        assert isinstance(part.numbering, Numbering), part.numbering
