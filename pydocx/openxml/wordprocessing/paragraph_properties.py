# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class ParagraphProperties(XmlModel):
    XML_TAG = 'pPr'

    parent_style = XmlChild(name='pStyle', attrname='val')
