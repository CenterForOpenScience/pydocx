# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class AlternateContent(XmlModel):
    XML_TAG = 'AlternateContent'
    children = XmlCollection('markup_compatibility.Fallback')
