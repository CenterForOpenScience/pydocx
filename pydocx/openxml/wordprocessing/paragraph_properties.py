# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.wordprocessing.numbering_properties import NumberingProperties  # noqa


class ParagraphProperties(XmlModel):
    XML_TAG = 'pPr'

    parent_style = XmlChild(name='pStyle', attrname='val')
    numbering_properties = XmlChild(type=NumberingProperties)
    justification = XmlChild(name='jc', attrname='val')
