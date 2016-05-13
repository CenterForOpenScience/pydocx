# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.markup_compatibility.fallback import Fallback


class AlternateContent(XmlModel):
    XML_TAG = 'AlternateContent'
    children = XmlCollection(Fallback)
