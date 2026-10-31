# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.graphic import Graphic
from pydocx.openxml.wordprocessing.document_properties import DocPr


class Inline(XmlModel):
    XML_TAG = 'inline'

    graphic = XmlChild(type=Graphic)
    DocPr = XmlChild(type=DocPr)
