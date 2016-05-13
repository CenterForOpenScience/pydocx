# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.picture import Picture


class Fallback(XmlModel):
    XML_TAG = 'Fallback'
    children = XmlCollection(Picture)
