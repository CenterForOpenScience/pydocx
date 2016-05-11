# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
# from pydocx.openxml.wordprocessing import Paragraph


class TxBxContent(XmlModel):
    XML_TAG = 'txbxContent'
    children = XmlCollection(
        'wordprocessing.Paragraph',
    )


class Textbox(XmlModel):
    XML_TAG = 'textbox'

    children = XmlCollection(
        TxBxContent,
    )
