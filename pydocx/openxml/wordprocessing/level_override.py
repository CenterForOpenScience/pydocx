# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute
from pydocx.openxml.wordprocessing.level import Level


class LevelOverride(XmlModel):
    XML_TAG = 'lvlOverride'

    level_id = XmlAttribute(name='ilvl')
    start_override = XmlChild(name='startOverride', attrname='val')
    level = XmlChild(type=Level)
