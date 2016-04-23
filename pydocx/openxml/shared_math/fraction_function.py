from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.numerator import Numerator
from pydocx.openxml.shared_math.denominator import Denominator


class FractionFunction(XmlModel):
    XML_TAG = 'f'
    children = XmlCollection(
        Numerator,
        Denominator
    )
