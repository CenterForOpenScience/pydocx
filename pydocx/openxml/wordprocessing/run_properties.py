# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.types import OnOff, Underline


class RunProperties(XmlModel):
    XML_TAG = 'rPr'

    bold = XmlChild(type=OnOff, name='b', attrname='val')
    italic = XmlChild(type=OnOff, name='i', attrname='val')
    underline = XmlChild(type=Underline, name='u', attrname='val')
    caps = XmlChild(type=OnOff, attrname='val')
    small_caps = XmlChild(type=OnOff, name='smallCaps', attrname='val')
    strike = XmlChild(type=OnOff, attrname='val')
    dstrike = XmlChild(type=OnOff, attrname='val')
    vanish = XmlChild(type=OnOff, attrname='val')
    hidden = XmlChild(type=OnOff, name='webHidden', attrname='val')
    vertical_align = XmlChild(name='vertAlign', attrname='val')
    parent_style = XmlChild(name='rStyle', attrname='val')
    pos = XmlChild(name='position', attrname='val')
    sz = XmlChild(name='sz', attrname='val')

    @property
    def position(self):
        if self.pos is None:
            return 0
        return int(self.pos)

    @property
    def size(self):
        if self.sz is None:
            return
        try:
            size = float(self.sz)
        except ValueError:
            size = None
        return size

    def is_superscript(self):
        return self.vertical_align == 'superscript'

    def is_subscript(self):
        return self.vertical_align == 'subscript'
