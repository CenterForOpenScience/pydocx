from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.function_properties import FunctionProperties


class FunctionApplyFunction(XmlModel):
    XML_TAG = 'func'

    children = XmlCollection(
        FunctionProperties,
        Element
    )


# solves circular import
from pydocx.openxml.shared_math.function_name import FunctionName  # noqa

FunctionApplyFunction.children.types.add(FunctionName)
