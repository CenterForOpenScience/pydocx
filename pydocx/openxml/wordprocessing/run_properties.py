# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, ChildTag
from pydocx.types import OnOff, Underline


class RunProperties(XmlModel):
    bold = ChildTag(type=OnOff, name='b', attrname='val')
    italic = ChildTag(type=OnOff, name='i', attrname='val')
    underline = ChildTag(type=Underline, name='u', attrname='val')
    caps = ChildTag(type=OnOff, attrname='val')
    small_caps = ChildTag(type=OnOff, name='smallCaps', attrname='val')
    strike = ChildTag(type=OnOff, attrname='val')
    dstrike = ChildTag(type=OnOff, attrname='val')
    vanish = ChildTag(type=OnOff, attrname='val')
    hidden = ChildTag(type=OnOff, name='webHidden', attrname='val')
    vertical_align = ChildTag(name='vertAlign', attrname='val')
    parent_style = ChildTag(name='rStyle', attrname='val')
    pos = ChildTag(name='position', attrname='val')
    sz = ChildTag(name='sz', attrname='val')

    @property
    def position(self):
        if self.pos is None:
            return 0
        return int(self.pos)

    @property
    def size(self):
        if self.sz is None:
            return
        return int(self.sz)
