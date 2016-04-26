from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.lower_limit_properties import LowerLimitProperties


class LowerLimitFunction(XmlModel):
    XML_TAG = 'limLow'
    children = XmlCollection(
        Element,
        LowerLimitProperties
    )

# solves circular import
from pydocx.openxml.shared_math.limit import Limit  # noqa

LowerLimitFunction.children.types.add(Limit)
