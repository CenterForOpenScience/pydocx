from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.base import Base
from pydocx.openxml.shared_math.equation_array_properties import EquationArrayProperties


class EquationArrayFunction(XmlModel):
    XML_TAG = 'eqArr'

    children = XmlCollection(
        Base,
        EquationArrayProperties
    )
