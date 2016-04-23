from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties


class BorderBoxProperties(XmlModel):

    XML_TAG = 'borderBoxPr'

    hide_top = XmlChild(name='hideTop', attrname='val')
    hide_bot = XmlChild(name='hideBot', attrname='val')
    hide_left = XmlChild(name='hideLeft', attrname='val')
    hide_right = XmlChild(name='hideRight', attrname='val')
    strike_h = XmlChild(name='strikeH', attrname='val')
    strike_v = XmlChild(name='strikeV', attrname='val')
    strike_bltr = XmlChild(name='strikeBLTR', attrname='val')
    strike_tlbr = XmlChild(name='strikeTLBR', attrname='val')

    children = XmlCollection(
        ControlProperties
    )
