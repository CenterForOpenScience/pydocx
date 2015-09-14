# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute, XmlCollection
from pydocx.openxml.wordprocessing.level import Level


class AbstractNum(XmlModel):
    XML_TAG = 'abstractNum'

    abstract_num_id = XmlAttribute(name='abstractNumId')
    name = XmlChild(attrname='val')

    levels = XmlCollection(Level)

    def __init__(self, **kwargs):
        super(AbstractNum, self).__init__(**kwargs)

        self._levels = {}

        for level in self.levels:
            self._levels[level.level_id] = level

    def get_level(self, level_id):
        return self._levels.get(level_id)
