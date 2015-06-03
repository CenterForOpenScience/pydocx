# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from itertools import islice

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.openxml.wordprocessing.br import Break
from pydocx.openxml.wordprocessing.drawing import Drawing
from pydocx.openxml.wordprocessing.picture import Picture
from pydocx.openxml.wordprocessing.no_break_hyphen import NoBreakHyphen
from pydocx.openxml.wordprocessing.text import Text
from pydocx.openxml.wordprocessing.deleted_text import DeletedText


class Run(XmlModel):
    XML_TAG = 'r'

    properties = XmlChild(type=RunProperties)

    children = XmlCollection(
        Break,
        NoBreakHyphen,
        Text,
        Drawing,
        Picture,
        DeletedText,
    )

    def _get_properties_inherited_from_parent_paragraph(self):
        from pydocx.openxml.wordprocessing.paragraph import Paragraph

        inherited_properties = {}

        if not self.container.style_definitions_part:
            return inherited_properties

        nearest_paragraphs = self.nearest_ancestors(Paragraph)
        parent_paragraph = list(islice(nearest_paragraphs, 0, 1))
        if parent_paragraph:
            parent_paragraph = parent_paragraph[0]
            style_stack = parent_paragraph.get_style_chain_stack()
            for style in reversed(list(style_stack)):
                if style.run_properties:
                    inherited_properties.update(
                        dict(style.run_properties.fields),
                    )
        return inherited_properties

    def _get_inherited_properties_from_parent_style(self):
        inherited_properties = {}

        properties = self.properties
        if not properties:
            return inherited_properties

        if not self.container.style_definitions_part:
            return properties

        styles_part = self.container.style_definitions_part

        parent_style = properties.parent_style
        if parent_style:
            style_stack = styles_part.get_style_chain_stack(
                'character',
                parent_style,
            )
            for style in reversed(list(style_stack)):
                if style and style.run_properties:
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
    def effective_properties(self):
        if not self.container.style_definitions_part:
            return self.properties

        inherited_properties = self.inherited_properties
        effective_properties = {}
        effective_properties.update(dict(inherited_properties.fields))
        if self.properties:
            effective_properties.update(dict(self.properties.fields))
        return RunProperties(**effective_properties)
