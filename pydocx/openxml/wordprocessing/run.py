# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.openxml.wordprocessing.br import Break
from pydocx.openxml.wordprocessing.no_break_hyphen import NoBreakHyphen
from pydocx.openxml.wordprocessing.text import Text


class Run(XmlModel):
    XML_TAG = 'r'

    properties = XmlChild(type=RunProperties)

    children = XmlCollection(
        Break,
        NoBreakHyphen,
        Text,
    )

    @property
    def effective_properties(self):
        properties = self.properties
        if not self.container.style_definitions_part:
            return properties

        styles_part = self.container.style_definitions_part

        parent_style = properties.parent_style
        effective_properties = {}
        # parent_paragraph = islice(run.nearest_ancestors(wordprocessing.Paragraph), 0, 1)  # noqa
        # if parent_paragraph:
        #    effective_properties.update(
        #        dict(parent_paragraph[0].effective_properties.run_properties.fields),  # noqa
        #    )
        if parent_style:
            effective_properties = styles_part._get_merged_style_chain(
                'character',
                parent_style,
            )
        effective_properties.update(dict(properties.fields))
        return RunProperties(**effective_properties)
