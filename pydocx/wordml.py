from __future__ import absolute_import

from pydocx.openxml import (
    OpenXmlPart,
    OpenXmlPackage,
)

from pydocx.utils import zip_path_join


class MainDocumentPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'officeDocument',
    ])

    @property
    def style_definitions_part(self):
        pass

    @property
    def numbering_definitions_part(self):
        pass

    @property
    def image_parts(self):
        pass


class WordprocessingDocument(OpenXmlPackage):
    namespace = '/'.join([
        'http://schemas.openxmlformats.org',
        'wordprocessingml',
        '2006',
        'main',
    ])

    def __init__(self, path):
        super(WordprocessingDocument, self).__init__(path=path)
        self._main_document_part = None

    @property
    def main_document_part(self):
        if self._main_document_part is None:
            self.load_parts()
        return self._main_document_part

    def load_parts(self):
        relationships = self.package.get_relationships_by_type(
            MainDocumentPart.relationship_type,
        )
        relationship = relationships[0]
        part_uri = zip_path_join(
            relationship.source_uri,
            relationship.target_uri,
        )
        self._main_document_part = MainDocumentPart(
            open_xml_package=self,
            uri=part_uri,
        )
        self.add_part(
            part=self._main_document_part,
            relationship_id=relationship.relationship_id,
        )


class Document(object):
    pass
