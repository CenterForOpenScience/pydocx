# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class Fallback(XmlModel):
    XML_TAG = 'Fallback'
    children = XmlCollection(allow_all_children=True)
