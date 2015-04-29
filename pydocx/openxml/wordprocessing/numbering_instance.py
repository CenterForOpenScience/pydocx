# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute, XmlCollection
from pydocx.openxml.wordprocessing.level_override import LevelOverride


class NumberingInstance(XmlModel):
    XML_TAG = 'num'

    num_id = XmlAttribute(name='numId')
    abstract_num_id = XmlChild(name='abstractNumId', attrname='val')

    level_overrides = XmlCollection(LevelOverride)
