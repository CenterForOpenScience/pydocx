# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.pictures.shape_properties import ShapeProperties
from pydocx.openxml.drawing.pictures.blip_fill import BlipFill


class Picture(XmlModel):
    XML_TAG = 'pic'

    shape_properties = XmlChild(type=ShapeProperties)
    blip_fill = XmlChild(type=BlipFill)
