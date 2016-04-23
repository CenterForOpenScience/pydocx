from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.base import Base
from pydocx.openxml.shared_math.upper_limit_properties import UpperLimitProperties


class UpperLimitFunction(XmlModel):
    XML_TAG = 'limUpp'
    children = XmlCollection(
        Base,
        UpperLimitProperties
    )


# solves circular import
from pydocx.openxml.shared_math.limit import Limit #  noqa

UpperLimitFunction.children.types.add(Limit)
