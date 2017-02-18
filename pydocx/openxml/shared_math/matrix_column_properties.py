from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.matrix_column_count import MatrixColumnCount
from pydocx.openxml.shared_math.matrix_column_justification import MatrixColumnJustification


class MatrixColumnProperties(XmlModel):
    XML_TAG = 'mcPr'

    children = XmlCollection(
        MatrixColumnCount,
        MatrixColumnJustification
    )
