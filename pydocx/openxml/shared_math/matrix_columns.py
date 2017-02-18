from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.matrix_column import MatrixColumn


class MatrixColumns(XmlModel):
    XML_TAG = 'mcs'

    children = XmlCollection(
        MatrixColumn
    )
