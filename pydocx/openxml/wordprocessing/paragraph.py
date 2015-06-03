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
from pydocx.openxml.wordprocessing.smart_tag_run import SmartTagRun
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun


class Paragraph(XmlModel):
    XML_TAG = 'p'

    properties = XmlChild(type=ParagraphProperties)

    children = XmlCollection(
        Run,
        Hyperlink,
        SmartTagRun,
        InsertedRun,
        DeletedRun,
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

    def get_style_chain_stack(self):
        if not self.properties:
            raise StopIteration

        parent_style = self.properties.parent_style
        if not parent_style:
            raise StopIteration

        stack = self.container.style_definitions_part.get_style_chain_stack(
            'paragraph',
            parent_style,
        )
        for result in stack:
            yield result

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
