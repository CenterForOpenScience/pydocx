# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.openxml.wordprocessing.br import Break
from pydocx.openxml.wordprocessing.drawing import Drawing
from pydocx.openxml.wordprocessing.field_char import FieldChar
from pydocx.openxml.wordprocessing.field_code import FieldCode
from pydocx.openxml.wordprocessing.picture import Picture
from pydocx.openxml.wordprocessing.no_break_hyphen import NoBreakHyphen
from pydocx.openxml.wordprocessing.text import Text
from pydocx.openxml.wordprocessing.tab_char import TabChar
from pydocx.openxml.wordprocessing.deleted_text import DeletedText
from pydocx.openxml.wordprocessing.footnote_reference import FootnoteReference
from pydocx.openxml.wordprocessing.footnote_reference_mark import FootnoteReferenceMark
from pydocx.openxml.wordprocessing.embedded_object import EmbeddedObject
from pydocx.openxml.markup_compatibility import AlternateContent
from pydocx.util.memoize import memoized


class Run(XmlModel):
    XML_TAG = 'r'

    properties = XmlChild(type=RunProperties)

    children = XmlCollection(
        EmbeddedObject,
        TabChar,
        Break,
        NoBreakHyphen,
        Text,
        Drawing,
        Picture,
        DeletedText,
        FootnoteReference,
        FootnoteReferenceMark,
        FieldChar,
        FieldCode,
        AlternateContent,
    )

    def get_style_chain_stack(self):
        if not self.properties:
            return

        parent_style = self.properties.parent_style
        if not parent_style:
            return

        # TODO the getattr is necessary because of footnotes. From the context
        # of a footnote, a paragraph's container is the footnote part, which
        # doesn't have access to the style_definitions_part
        part = getattr(self.container, 'style_definitions_part', None)
        if part:
            style_stack = part.get_style_chain_stack('character', parent_style)
            for result in style_stack:
                yield result

    def _get_properties_inherited_from_parent_paragraph(self):
        from pydocx.openxml.wordprocessing.paragraph import Paragraph

        inherited_properties = {}

        parent_paragraph = self.get_first_ancestor(Paragraph)
        if parent_paragraph:
            style_stack = parent_paragraph.get_style_chain_stack()
            for style in reversed(list(style_stack)):
                if style.run_properties:
                    inherited_properties.update(
                        dict(style.run_properties.fields),
                    )
        return inherited_properties

    def _get_inherited_properties_from_parent_style(self):
        inherited_properties = {}
        style_stack = self.get_style_chain_stack()
        for style in reversed(list(style_stack)):
            if style.run_properties:
                inherited_properties.update(
                    dict(style.run_properties.fields),
                )
        return inherited_properties

    @property
    def inherited_properties(self):
        properties = {}
        properties.update(
            self._get_properties_inherited_from_parent_paragraph(),
        )
        properties.update(
            self._get_inherited_properties_from_parent_style(),
        )
        return RunProperties(**properties)

    @property
    @memoized
    def effective_properties(self):
        inherited_properties = self.inherited_properties
        effective_properties = {}
        effective_properties.update(dict(inherited_properties.fields))
        if self.properties:
            effective_properties.update(dict(self.properties.fields))
        return RunProperties(**effective_properties)
