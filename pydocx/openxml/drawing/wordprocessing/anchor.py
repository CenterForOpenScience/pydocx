# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.graphic import Graphic


class Anchor(XmlModel):
    XML_TAG = 'anchor'

    graphic = XmlChild(type=Graphic)
