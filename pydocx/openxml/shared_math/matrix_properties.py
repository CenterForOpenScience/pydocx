from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.base_justification import BaseJustification
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.hide_placeholders import HidePlaceholders
from pydocx.openxml.shared_math.matrix_columns import MatrixColumns
from pydocx.openxml.shared_math.matrix_column_spacing import MatrixColumnSpacing
from pydocx.openxml.shared_math.matrix_column_gap_rule import MatrixColumnGapRule
from pydocx.openxml.shared_math.matrix_column_gap import MatrixColumnGap
from pydocx.openxml.shared_math.row_spacing import RowSpacing
from pydocx.openxml.shared_math.row_spacing_rule import RowSpacingRule


class MatrixProperties(XmlModel):

    XML_TAG = 'mPr'
    base_jc = XmlChild(type=BaseJustification, attrname='val')
    plc_hide = XmlChild(type=HidePlaceholders, attrname='val')
    rsp_rule = XmlChild(type=RowSpacingRule, attrname='val')
    cgp_rule = XmlChild(type=MatrixColumnGapRule, attrname='val')
    rsp = XmlChild(type=RowSpacing, attrname='val')
    csp = XmlChild(type=MatrixColumnSpacing, attrname='val')
    cgp = XmlChild(type=MatrixColumnGap, attrname='val')
    children = XmlCollection(
        ControlProperties,
        MatrixColumns,
    )
