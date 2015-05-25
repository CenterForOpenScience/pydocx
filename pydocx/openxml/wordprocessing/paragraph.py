# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.paragraph_properties import ParagraphProperties  # noqa
from pydocx.openxml.wordprocessing.run import Run


class Paragraph(XmlModel):
    XML_TAG = 'p'

    properties = XmlChild(type=ParagraphProperties)

    children = XmlCollection(
        Run,
    )

    def __init__(self, **kwargs):
        self._effective_properties = None
        super(Paragraph, self).__init__(**kwargs)

    @property
    def effective_properties(self):
        if not self._effective_properties:
            self._effective_properties = self.load_effective_properties()
        return self._effective_properties

    def load_effective_properties(self):
        # TODO need to actually build this
        effective_properties = self.properties
        self._effective_properties = effective_properties
        return effective_properties

    def get_numbering_definition(self, numbering):
        # TODO add memoization
        if not self.effective_properties:
            return
        if not self.effective_properties.numbering_properties:
            return
        numbering_properties = self.effective_properties.numbering_properties

        return numbering.get_numbering_definition(
            num_id=numbering_properties.num_id,
        )

    def get_numbering_level(self, numbering):
        # TODO add memoization
        if not self.effective_properties:
            return
        if not self.effective_properties.numbering_properties:
            return

        numbering_properties = self.effective_properties.numbering_properties

        numbering_definition = self.get_numbering_definition(numbering)
        if numbering_definition:
            return numbering_definition.get_level(
                level_id=numbering_properties.level_id,
            )
