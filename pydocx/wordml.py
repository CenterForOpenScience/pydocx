from __future__ import absolute_import

from pydocx.openxml import (
    OpenXmlPart,
    OpenXmlPackage,
)


class ImagePart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'image',
    ])


class StyleDefinitionsPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'styles',
    ])


class NumberingDefinitionsPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'numbering',
    ])


class FontTablePart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'fontTable',
    ])


class MainDocumentPart(OpenXmlPart):
    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'officeDocument',
    ])

    child_part_types = [
        FontTablePart,
        ImagePart,
        NumberingDefinitionsPart,
        StyleDefinitionsPart,
    ]

    def get_relationship_lookup(self):
        package_lookup = self.open_xml_package.get_relationship_lookup()
        return package_lookup.get_part(self.uri)

    @property
    def style_definitions_part(self):
        return self.get_part_of_class_type(part_class=StyleDefinitionsPart)

    @property
    def numbering_definitions_part(self):
        return self.get_part_of_class_type(part_class=NumberingDefinitionsPart)

    @property
    def font_table_part(self):
        return self.get_part_of_class_type(part_class=FontTablePart)

    @property
    def image_parts(self):
        return self.get_parts_of_type(
            relationship_type=ImagePart.relationship_type,
        )


class WordprocessingDocument(OpenXmlPackage):
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


class Document(object):
    pass
