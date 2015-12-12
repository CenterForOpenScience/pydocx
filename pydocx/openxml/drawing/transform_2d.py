# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute
from pydocx.openxml.drawing.extents import Extents


class Transform2D(XmlModel):
    XML_TAG = 'xfrm'

    extents = XmlChild(type=Extents)
    rotate = XmlAttribute(name='rot', default=None)
