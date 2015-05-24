# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.paragraph import Paragraph


class Body(XmlModel):
    XML_TAG = 'body'

    children = XmlCollection(
        Paragraph,
    )

    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        self._children_lookup = dict(
            (child, i)
            for i, child in enumerate(self.children)
        )

    def __iter__(self):
        for node in self.children:
            yield node

    def next_child(self, child):
        index = self._children_lookup.get(child, None)
        if index is None:
            return
        next_child_index = index + 1
        if next_child_index >= len(self.children):
            return
        return self.children[next_child_index]

    def previous_child(self, child):
        index = self._children_lookup.get(child, None)
        if index is None:
            return
        previous_child_index = index - 1
        if previous_child_index < 0:
            return
        return self.children[previous_child_index]
