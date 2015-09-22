# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.vml.shape import Shape


class EmbeddedObject(XmlModel):
    """
    reference: http://www.datypic.com/sc/ooxml/e-w_object-1.html
    """

    XML_TAG = 'object'

    children = XmlCollection(Shape)
