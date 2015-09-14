# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlAttribute


class Extents(XmlModel):
    XML_TAG = 'ext'

    length = XmlAttribute(name='cx')
    width = XmlAttribute(name='cy')
