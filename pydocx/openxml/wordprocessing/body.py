# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.paragraph import Paragraph


class Body(XmlModel):
    XML_TAG = 'body'

    children = XmlCollection(
        Paragraph,
    )
