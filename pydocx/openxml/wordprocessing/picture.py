# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.vml import Shape


class Picture(XmlModel):
    XML_TAG = 'pict'

    children = XmlCollection(Shape)
