from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties


class GroupCharacterProperties(XmlModel):
    XML_TAG = 'groupChrPr'
    chr = XmlChild(name='chr', attrname='val')
    pos = XmlChild(name='pos', attrname='val')
    vert_jc = XmlChild(name='vertJc', attrname='val')
    children = XmlCollection(
        ControlProperties,
    )
