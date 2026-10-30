# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.types import OnOff
from pydocx.models import XmlModel, XmlChild, XmlAttribute
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.openxml.wordprocessing.paragraph_properties import ParagraphProperties


class Style(XmlModel):
    XML_TAG = 'style'

    style_type = XmlAttribute(name='type', default='paragraph')
    style_default = XmlAttribute(type=OnOff, name='default', default='0')
    style_id = XmlAttribute(name='styleId', default='')
    name = XmlChild(attrname='val', default='')
    run_properties = XmlChild(type=RunProperties)
    paragraph_properties = XmlChild(type=ParagraphProperties)
    parent_style = XmlChild(name='basedOn', attrname='val')

    def is_a_heading(self):
        if not self.name:
            return False
        return self.name.lower().startswith('heading')
