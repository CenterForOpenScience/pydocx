from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.matrix_properties import MatrixProperties
# from pydocx.openxml.shared_math.matrix_row import MatrixRow


class MatrixFunction(XmlModel):

    XML_TAG = 'm'
    children = XmlCollection(
        MatrixProperties,
        # MatrixRow
    )
