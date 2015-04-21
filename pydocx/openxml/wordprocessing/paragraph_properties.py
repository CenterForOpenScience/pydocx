# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, ChildTag


class ParagraphProperties(XmlModel):
    parent_style = ChildTag(name='pStyle', attrname='val')
