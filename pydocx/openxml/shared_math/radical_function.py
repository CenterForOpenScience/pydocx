from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.degree import Degree
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.radical_properties import RadicalProperties


class RadicalFunction(XmlModel):
    XML_TAG = 'rad'
    children = XmlCollection(
        Degree,
        Element,
        RadicalProperties,
    )
