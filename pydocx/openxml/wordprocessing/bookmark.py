# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlAttribute


class Bookmark(XmlModel):
    XML_TAG = 'bookmarkStart'

    name = XmlAttribute(name='name')
