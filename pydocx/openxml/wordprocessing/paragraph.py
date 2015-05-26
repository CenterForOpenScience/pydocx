# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.hyperlink import Hyperlink
from pydocx.openxml.wordprocessing.paragraph_properties import ParagraphProperties  # noqa
from pydocx.openxml.wordprocessing.run import Run


class Paragraph(XmlModel):
    XML_TAG = 'p'

    properties = XmlChild(type=ParagraphProperties)

    children = XmlCollection(
        Run,
        Hyperlink,
    )

    def __init__(self, **kwargs):
        super(Paragraph, self).__init__(**kwargs)
        self._effective_properties = None

    @property
    def effective_properties(self):
        if not self._effective_properties:
            properties = self.properties
            self._effective_properties = properties
        return self._effective_properties

    def get_numbering_definition(self):
        # TODO add memoization
        if not self.container.numbering_definitions_part:
            return
        numbering = self.container.numbering_definitions_part.numbering
        if not self.effective_properties:
            return
        numbering_properties = self.effective_properties.numbering_properties
        if not numbering_properties:
            return
        return numbering.get_numbering_definition(
            num_id=numbering_properties.num_id,
        )

    def get_numbering_level(self):
        # TODO add memoization
        numbering_definition = self.get_numbering_definition()
        if not numbering_definition:
            return
        if not self.effective_properties:
            return
        numbering_properties = self.effective_properties.numbering_properties
        if not numbering_properties:
            return
        return numbering_definition.get_level(
            level_id=numbering_properties.level_id,
        )
