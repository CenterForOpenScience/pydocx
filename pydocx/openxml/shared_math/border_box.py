from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.border_box_properties import BorderBoxProperties
from pydocx.openxml.shared_math.element import Element


class BorderBox(XmlModel):
    XML_TAG = 'borderBox'

    children = XmlCollection(
        BorderBoxProperties,
        Element
    )
