from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.sub import Sub
from pydocx.openxml.shared_math.subscript_properties import SubscriptProperties


class SubscriptFunction(XmlModel):
    XML_TAG = 'sSub'

    children = XmlCollection(
        Element,
        Sub,
        SubscriptProperties
    )
