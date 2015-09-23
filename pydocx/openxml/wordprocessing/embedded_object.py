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
    reference:  https://msdn.microsoft.com/en-us/library/documentformat.openxml
    .wordprocessing.embeddedobject%28v=office.15%29.aspx
    """

    XML_TAG = 'object'

    children = XmlCollection(Shape)
