from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.show import Show
from pydocx.openxml.shared_math.zero_width import ZeroWidth
from pydocx.openxml.shared_math.zero_ascent import ZeroAscent
from pydocx.openxml.shared_math.zero_descent import ZeroDescent
from pydocx.openxml.shared_math.transparent import Transparent


class PhantomProperties(XmlModel):

    XML_TAG = 'phantPr'

    show = XmlChild(type=Show, attrname='val')
    zero_wid = XmlChild(type=ZeroWidth, attrname='val')
    zero_asc = XmlChild(type=ZeroAscent, attrname='val')
    zero_desc = XmlChild(type=ZeroDescent, attrname='val')
    transp = XmlChild(type=Transparent, attrname='val')

    children = XmlCollection(
        ControlProperties
    )
