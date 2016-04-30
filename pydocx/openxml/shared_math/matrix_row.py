from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element


class MatrixRow(XmlModel):
    XML_TAG = 'mr'

    children = XmlCollection(
        Element
    )
