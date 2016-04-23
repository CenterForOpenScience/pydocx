from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

# incomplete
from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties
# from pydocx.openxml.shared_math.matrix_columns import MatrixColumns
from pydocx.openxml.shared_math.row_spacing import RowSpacing


class MatrixProperties(XmlModel):

    XML_TAG = 'mPr'
    base_jc = XmlChild(name='baseJc', attrname='val')
    children = XmlCollection(
        ControlProperties,
        RowSpacing
    )
