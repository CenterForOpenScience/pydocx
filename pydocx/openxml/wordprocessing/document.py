# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute
from pydocx.openxml.wordprocessing.body import Body


class Document(XmlModel):
    XML_TAG = 'document'

    conformance = XmlAttribute(name='conformance')
    body = XmlChild(type=Body)
