from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.bar_properties import BarProperties
from pydocx.openxml.shared_math.base import Base


class Bar(XmlModel):
    XML_TAG = 'bar'
    children = XmlCollection(
        BarProperties,
        Base
    )
