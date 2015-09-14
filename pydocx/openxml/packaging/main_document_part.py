# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.font_table_part import FontTablePart
from pydocx.openxml.packaging.footnotes_part import FootnotesPart
from pydocx.openxml.packaging.image_part import ImagePart
from pydocx.openxml.packaging.numbering_definitions_part import NumberingDefinitionsPart  # noqa
from pydocx.openxml.packaging.open_xml_part import OpenXmlPart
from pydocx.openxml.packaging.style_definitions_part import StyleDefinitionsPart  # noqa
from pydocx.openxml.wordprocessing import Document


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
        FootnotesPart,
        ImagePart,
        NumberingDefinitionsPart,
        StyleDefinitionsPart,
    ]

    def __init__(self, *args, **kwargs):
        super(MainDocumentPart, self).__init__(*args, **kwargs)
        self._document = None

    @property
    def document(self):
        if not self._document:
            self._document = self.load_document()
        return self._document

    def load_document(self):
        self._document = Document.load(self.root_element, container=self)
        return self._document

    def get_relationship_lookup(self):
        package_lookup = self.open_xml_package.get_relationship_lookup()
        return package_lookup.get_part(self.uri)

    @property
    def style_definitions_part(self):
        part = self.get_part_of_class_type(part_class=StyleDefinitionsPart)
        if part is None:
            part = StyleDefinitionsPart(
                uri=None,
                open_xml_package=self.open_xml_package,
            )
            self.add_part(part)
        return part

    @property
    def numbering_definitions_part(self):
        part = self.get_part_of_class_type(part_class=NumberingDefinitionsPart)
        if part is None:
            part = NumberingDefinitionsPart(
                uri=None,
                open_xml_package=self.open_xml_package,
            )
            self.add_part(part)
        return part

    @property
    def font_table_part(self):
        return self.get_part_of_class_type(part_class=FontTablePart)

    @property
    def image_parts(self):
        return self.get_parts_of_type(
            relationship_type=ImagePart.relationship_type,
        )

    @property
    def footnotes_part(self):
        return self.get_part_of_class_type(part_class=FootnotesPart)
