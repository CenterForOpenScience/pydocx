from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties


class BarProperties(XmlModel):
    XML_TAG = 'barPr'
    pos = XmlChild(name='pos', attrname='val')
    children = XmlCollection(
        ControlProperties
    )
