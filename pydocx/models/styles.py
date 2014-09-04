from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict

from pydocx.models import XmlModel, ChildTag, Attribute
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


class ParagraphProperties(XmlModel):
    parent_style = ChildTag(name='pStyle', attrname='val')


class Style(XmlModel):
    style_type = Attribute(name='type', default='paragraph')
    style_id = Attribute(name='styleId', default='')
    name = ChildTag(attrname='val', default='')
    run_properties = ChildTag(type=RunProperties, name='rPr')
    parent_style = ChildTag(name='basedOn', attrname='val')


class Styles(object):
    def __init__(self, styles=None):
        if styles is None:
            styles = []
        self.styles = styles
        styles_by_type = defaultdict(dict)
        for style in self.styles:
            styles_by_type[style.style_type][style.style_id] = style
        self.styles_by_type = dict(styles_by_type)

    @staticmethod
    def load(root):
        styles = []
        for element in root:
            if element.tag == 'style':
                style = Style.load(element)
                styles.append(style)
        return Styles(styles)

    def get_styles_by_type(self, style_type):
        return self.styles_by_type.get(style_type, {})
