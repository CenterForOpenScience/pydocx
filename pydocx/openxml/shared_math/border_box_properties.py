from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.hide_bottom import HideBottom
from pydocx.openxml.shared_math.hide_left import HideLeft
from pydocx.openxml.shared_math.hide_right import HideRight
from pydocx.openxml.shared_math.hide_top import HideTop
from pydocx.openxml.shared_math.strike_h import StrikeH
from pydocx.openxml.shared_math.strike_v import StrikeV
from pydocx.openxml.shared_math.strike_bltr import StrikeBLTR
from pydocx.openxml.shared_math.strike_tlbr import StrikeTLBR


class BorderBoxProperties(XmlModel):

    XML_TAG = 'borderBoxPr'

    hide_top = XmlChild(type=HideTop, attrname='val')
    hide_bot = XmlChild(type=HideBottom, attrname='val')
    hide_left = XmlChild(type=HideLeft, attrname='val')
    hide_right = XmlChild(type=HideRight, attrname='val')
    strike_h = XmlChild(type=StrikeH, attrname='val')
    strike_v = XmlChild(type=StrikeV, attrname='val')
    strike_bltr = XmlChild(type=StrikeBLTR, attrname='val')
    strike_tlbr = XmlChild(type=StrikeTLBR, attrname='val')

    children = XmlCollection(
        ControlProperties
    )
