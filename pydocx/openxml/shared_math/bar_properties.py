from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.position import Position


class BarProperties(XmlModel):
    XML_TAG = 'barPr'

    pos = XmlChild(type=Position, attrname='val')
    children = XmlCollection(
        ControlProperties
    )
