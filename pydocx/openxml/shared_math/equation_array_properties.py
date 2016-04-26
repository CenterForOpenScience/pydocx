from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.base_justification import BaseJustification
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.maximum_distribution import MaximumDistribution
from pydocx.openxml.shared_math.object_distribution import ObjectDistribution
from pydocx.openxml.shared_math.row_spacing_rule import RowSpacingRule
from pydocx.openxml.shared_math.row_spacing import RowSpacing


class EquationArrayProperties(XmlModel):
    XML_TAG = 'eqArrPr'

    base_jc = XmlChild(type=BaseJustification, attrname='val')
    rsp_rule = XmlChild(type=RowSpacingRule, attrname='val')
    rsp = XmlChild(type=RowSpacing, attrname='val')
    children = XmlCollection(
        MaximumDistribution,
        ObjectDistribution,
        ControlProperties
    )
