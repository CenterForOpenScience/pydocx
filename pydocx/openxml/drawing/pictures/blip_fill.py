# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.blip import Blip


class BlipFill(XmlModel):
    XML_TAG = 'blipFill'

    blip = XmlChild(type=Blip)
