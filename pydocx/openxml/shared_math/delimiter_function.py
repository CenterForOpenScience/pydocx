from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.delimiter_properties import DelimiterProperties


class DelimiterFunction(XmlModel):
    XML_TAG = 'd'

    children = XmlCollection(
        Element,
        DelimiterProperties
    )
