from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.matrix_column_properties import MatrixColumnProperties


class MatrixColumn(XmlModel):
    XML_TAG = 'mc'

    children = XmlCollection(
        MatrixColumnProperties
    )
