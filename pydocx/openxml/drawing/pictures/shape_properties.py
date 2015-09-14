# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.transform_2d import Transform2D


class ShapeProperties(XmlModel):
    XML_TAG = 'spPr'

    xfrm = XmlChild(type=Transform2D)
