# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlAttribute


class ImageData(XmlModel):
    XML_TAG = 'imagedata'

    # TODO We need namespaced attributes, because of conflicts like this. This
    # attribute is in the relationship namespace, and there's another attribute
    # named "id" which is in the default (in this case VML) namespace.
    # See https://msdn.microsoft.com/en-us/library/documentformat.openxml.vml.imagedata%28v=office.14%29.aspx  # noqa
    relationship_id = XmlAttribute(name='id')

    def get_picture_extents(self):
        style = self.parent.get_style()
        width = style.get('width', 0)
        height = style.get('height', 0)
        # TODO if width/height are missing units, "px" is implied
        return width, height
