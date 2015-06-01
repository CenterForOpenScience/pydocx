# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.graphic_data import GraphicData


class Graphic(XmlModel):
    XML_TAG = 'graphic'

    graphic_data = XmlChild(type=GraphicData)
