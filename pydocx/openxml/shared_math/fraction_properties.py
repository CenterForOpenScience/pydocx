from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.type import Type


class FractionProperties(XmlModel):

    XML_TAG = 'fPr'
    type = XmlChild(type=Type, attrname='val')
    children = XmlCollection(
        ControlProperties
    )
