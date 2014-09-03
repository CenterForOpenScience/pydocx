from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml import (
    OpenXmlPart,
    OpenXmlPackage,
)


class ImagePart(OpenXmlPart):
    '''
    Represents an image part relationship within a Word document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.imagepart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'image',
    ])


class StyleDefinitionsPart(OpenXmlPart):
    '''
    Represents style definitions within a Word document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.styledefinitionspart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'styles',
    ])


class NumberingDefinitionsPart(OpenXmlPart):
    '''
    Represents the list numbering definitions within a document container.
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'numbering',
    ])


class FontTablePart(OpenXmlPart):
    '''
    Represents the fonts associated within a document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.fonttablepart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'fontTable',
    ])


class MainDocumentPart(OpenXmlPart):
    '''
    Represents the actual document XML tree within a Word document container.
    This OpenXmlPart exposes several child parts for styles, numbering, fonts
    and images.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.maindocumentpart%28v=office.14%29.aspx  # noqa
    '''

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
