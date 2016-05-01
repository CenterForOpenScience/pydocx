from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlCollection
from pydocx.openxml.shared_math.character import Character
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.grow import Grow
from pydocx.openxml.shared_math.sub_hide import HideSubscript
from pydocx.openxml.shared_math.sup_hide import HideSuperscript
from pydocx.openxml.shared_math.nary_limit_location import NaryLimitLocation


class NaryProperties(XmlModel):

    chr = XmlChild(type=Character, attrname='val')
    lim_loc = XmlChild(type=NaryLimitLocation, attrname='val')
    grow = XmlChild(type=Grow, attrname='val')
    sub_hide = XmlChild(type=HideSubscript, attrname='val')
    sup_hide = XmlChild(type=HideSuperscript, attrname='val')
    children = XmlCollection(
        ControlProperties
    )
