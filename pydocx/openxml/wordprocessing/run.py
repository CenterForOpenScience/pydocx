# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.util.memoize import memoized


class Run(XmlModel):
    XML_TAG = 'r'

    properties = XmlChild(type=RunProperties)

    children = XmlCollection(
        'wordprocessing.EmbeddedObject',
        'wordprocessing.TabChar',
        'wordprocessing.Break',
        'wordprocessing.NoBreakHyphen',
        'wordprocessing.Text',
        'wordprocessing.Drawing',
        'wordprocessing.Picture',
        'wordprocessing.DeletedText',
        'wordprocessing.FootnoteReference',
        'wordprocessing.FootnoteReferenceMark',
        'wordprocessing.FieldChar',
        'wordprocessing.FieldCode',
        'markup_compatibility.AlternateContent',
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
