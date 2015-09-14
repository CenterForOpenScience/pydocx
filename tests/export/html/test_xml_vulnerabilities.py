# coding: utf-8

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from nose import SkipTest

from pydocx.test import DocumentGeneratorTestCase
from pydocx.test.utils import WordprocessingDocumentFactory
from pydocx.openxml.packaging import MainDocumentPart


class XMLVulnerabilitiesTestCase(DocumentGeneratorTestCase):
    def test_exponential_entity_expansion(self):
        try:
            import defusedxml
        except ImportError:
            defusedxml = None

        if defusedxml is None:
            raise SkipTest('This test case only applies when using defusedxml')

        document_xml = '''
            <p>
              <r>
                <t>&c;</t>
              </r>
            </p>
        '''
        xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xml [
 <!ENTITY a "123">
 <!ENTITY b "&a;&a;">
 <!ENTITY c "&b;&b;">
]>
        '''
        document = WordprocessingDocumentFactory(xml_header=xml_header)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>123123123123</p>'
        try:
            self.assert_document_generates_html(document, expected_html)
            raise AssertionError(
                'Expected "EntitiesForbidden" exception did not occur',
            )
        except defusedxml.EntitiesForbidden:
            pass

    def test_entity_blowup(self):
        try:
            import defusedxml
        except ImportError:
            defusedxml = None

        if defusedxml is None:
            raise SkipTest('This test case only applies when using defusedxml')

        document_xml = '''
            <p>
              <r>
                <t>&a;</t>
              </r>
            </p>
        '''
        xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xml [
 <!ENTITY a "123">
]>
        '''
        document = WordprocessingDocumentFactory(xml_header=xml_header)
        document.add(MainDocumentPart, document_xml)

        expected_html = '<p>123</p>'
        try:
            self.assert_document_generates_html(document, expected_html)
            raise AssertionError(
                'Expected "EntitiesForbidden" exception did not occur',
            )
        except defusedxml.EntitiesForbidden:
            pass
