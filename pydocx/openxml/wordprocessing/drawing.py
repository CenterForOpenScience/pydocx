# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.drawing.wordprocessing.anchor import Anchor
from pydocx.openxml.drawing.wordprocessing.inline import Inline


class Drawing(XmlModel):
    XML_TAG = 'drawing'

    anchor = XmlChild(type=Anchor)
    inline = XmlChild(type=Inline)

    @property
    def graphic(self):
        try:
            return self.anchor.graphic
        except AttributeError:
            pass
        try:
            return self.inline.graphic
        except AttributeError:
            pass

    def get_picture_extents(self):
        graphic = self.graphic
        length = 0
        width = 0
        extents = None
        try:
            extents = graphic.graphic_data.picture.shape_properties.xfrm.extents  # noqa
        except AttributeError:
            pass
        if extents:
            try:
                length = int(extents.length)
                width = int(extents.width)
            except (TypeError, ValueError):
                length = width = 0
        return length, width

    def get_picture_rotate_angle(self):
        graphic = self.graphic
        rotate = None
        try:
            rotate = graphic.graphic_data.picture.shape_properties.xfrm.rotate  # noqa
        except AttributeError:
            pass
        if rotate:
            try:
                # according to this link
                # http://www.ecma-international.org/publications/standards/Ecma-376.htm
                # §20.1.10.3
                #
                # "This simple type represents an angle in 60,000ths of a degree.
                # Positive angles are clockwise (i.e., towards the positive y axis);
                # negative angles are counter-clockwise (i.e., towards the negative y axis)."

                rotate = int(int(rotate) / 60000)
            except (TypeError, ValueError):
                rotate = None

        return rotate

    def get_picture_relationship_id(self):
        graphic = self.graphic
        blip = None
        try:
            blip = graphic.graphic_data.picture.blip_fill.blip
        except AttributeError:
            pass
        if blip:
            if blip.embedded_picture_id:
                return blip.embedded_picture_id
            return blip.linked_picture_id
