from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlAttribute


class DocPr(XmlModel):
    XML_TAG = 'docPr'

    title = XmlAttribute(name='title')
    descr = XmlAttribute(name='descr')
