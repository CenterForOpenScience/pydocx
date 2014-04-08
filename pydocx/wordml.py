from __future__ import absolute_import

from pydocx.openxml import (
    OpenXmlPart,
    OpenXmlPackage,
)

from pydocx.utils import zip_path_join


class ChildPartLoader(object):
    child_part_types = NotImplemented

    def get_relationship_lookup(self):
        raise NotImplementedError

    def load_parts(self):
        relationship_lookup = self.get_relationship_lookup()
        for child_part_type in self.child_part_types:
            relationships = relationship_lookup.get_relationships_by_type(
                child_part_type.relationship_type,
            )
            relationship = relationships[0]
            part_uri = zip_path_join(
                relationship.source_uri,
                relationship.target_uri,
            )
            part = child_part_type(
                open_xml_package=self,
                uri=part_uri,
            )
            self.add_part(
                part=part,
                relationship_id=relationship.relationship_id,
            )


class StyleDefinitionsPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'styles',
    ])


class MainDocumentPart(ChildPartLoader, OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'officeDocument',
    ])

    child_part_types = [
        StyleDefinitionsPart,
    ]

    def get_relationship_lookup(self):
        return self.package.get_part(self.uri)

    @property
    def style_definitions_part(self):
        self.ensure_parts_are_loaded()
        return self.get_parts_of_type(
            StyleDefinitionsPart.relationship_type,
        )[0]

    @property
    def numbering_definitions_part(self):
        pass

    @property
    def image_parts(self):
        pass


class WordprocessingDocument(ChildPartLoader, OpenXmlPackage):
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
        self.ensure_parts_are_loaded()
        return self.get_parts_of_type(
            MainDocumentPart.relationship_type,
        )[0]


class Document(object):
    pass
