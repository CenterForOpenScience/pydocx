# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.pictures.picture import Picture


class GraphicData(XmlModel):
    XML_TAG = 'graphicData'

    picture = XmlChild(type=Picture)
