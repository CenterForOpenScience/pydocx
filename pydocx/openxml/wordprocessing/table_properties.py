# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class TableProperties(XmlModel):
    XML_TAG = 'tblPr'

    parent_style = XmlChild(name='tblStyle', attrname='val')
