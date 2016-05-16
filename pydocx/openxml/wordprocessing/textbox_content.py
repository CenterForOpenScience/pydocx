# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class TxBxContent(XmlModel):
    XML_TAG = 'txbxContent'
    children = XmlCollection(
        'wordprocessing.Paragraph',
    )
