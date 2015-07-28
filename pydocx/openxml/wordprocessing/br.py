# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlAttribute, XmlModel


class Break(XmlModel):
    XML_TAG = 'br'

    break_type = XmlAttribute(name='type')

    def is_page_break(self):
        return self.break_type == 'page'
