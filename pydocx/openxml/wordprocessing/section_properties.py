# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class SectionProperties(XmlModel):
    XML_TAG = 'sectPr'

    page_size = XmlChild(name='pgSz', type=lambda el: dict(el.attrib))
