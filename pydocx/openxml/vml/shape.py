# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlAttribute
from pydocx.openxml.vml.image_data import ImageData


class Shape(XmlModel):
    XML_TAG = 'shape'

    style = XmlAttribute()
    children = XmlCollection(ImageData)

    # TODO perhaps we could have a prepare_style, or clean_style convention?

    def get_style(self):
        if self.style:
            return dict(
                item.split(':', 1)
                for item in self.style.split(';')
                if item
            )
        return {}
