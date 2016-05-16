# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class Textbox(XmlModel):
    XML_TAG = 'textbox'

    children = XmlCollection(
        'wordprocessing.TxBxContent',
    )
