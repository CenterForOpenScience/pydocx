from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.character import Character
from pydocx.openxml.shared_math.control_properties import ControlProperties


class AccentProperties(XmlModel):
    XML_TAG = 'accPr'

    chr = XmlChild(type=Character, attrname='val')
    children = XmlCollection(
        ControlProperties
    )
