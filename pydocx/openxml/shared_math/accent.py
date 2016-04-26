from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.accent_properties import AccentProperties
from pydocx.openxml.shared_math.element import Element


class Accent(XmlModel):
    XML_TAG = 'acc'

    children = XmlCollection(
        AccentProperties,
        Element
    )
