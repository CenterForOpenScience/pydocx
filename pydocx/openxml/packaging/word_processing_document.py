# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.main_document_part import MainDocumentPart
from pydocx.openxml.packaging.open_xml_package import OpenXmlPackage


class WordprocessingDocument(OpenXmlPackage):
    '''
    The top-most level of a Word document container which is an OpenXmlPackage
    that exposes a single child part, `main_document_part`.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.wordprocessingdocument%28v=office.14%29.aspx  # noqa
    '''

    namespace = '/'.join([
        'http://schemas.openxmlformats.org',
        'wordprocessingml',
        '2006',
        'main',
    ])

    child_part_types = [
        MainDocumentPart,
    ]

    def get_relationship_lookup(self):
        return self.package

    @property
    def main_document_part(self):
        return self.get_part_of_class_type(part_class=MainDocumentPart)
