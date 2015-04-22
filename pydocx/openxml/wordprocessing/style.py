# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, ChildTag, Attribute
from pydocx.openxml.wordprocessing.run_properties import RunProperties


class Style(XmlModel):
    style_type = Attribute(name='type', default='paragraph')
    style_id = Attribute(name='styleId', default='')
    name = ChildTag(attrname='val', default='')
    run_properties = ChildTag(type=RunProperties, name='rPr')
    parent_style = ChildTag(name='basedOn', attrname='val')
