from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.base import Base
from pydocx.openxml.shared_math.box_properties import BoxProperties


class Box(XmlModel):

    XML_TAG = 'box'
    children = XmlCollection(
        Base,
        BoxProperties
    )
