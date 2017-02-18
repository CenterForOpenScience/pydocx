from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.character import Character
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.position import Position
from pydocx.openxml.shared_math.vertical_justification import VerticalJustification


class GroupCharacterProperties(XmlModel):
    XML_TAG = 'groupChrPr'

    chr = XmlChild(type=Character, attrname='val')
    pos = XmlChild(type=Position, attrname='val')
    vert_jc = XmlChild(type=VerticalJustification, attrname='val')
    children = XmlCollection(
        ControlProperties,
    )
