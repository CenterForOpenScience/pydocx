# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.vml.image_data import ImageData


class Rect(XmlModel):
    XML_TAG = 'rect'

    children = XmlCollection(ImageData, 'vml.Textbox')
