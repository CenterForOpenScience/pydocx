from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.control_properties import ControlProperties


class BoxProperties(XmlModel):

    XML_TAG = 'boxPr'

    op_emu = XmlChild(name='opEmu', attrname='val')
    no_break = XmlChild(name='noBreak', attrname='val')
    diff = XmlChild(name='diff', attrname='val')
    brk = XmlChild(name='brk', attrname='val')
    aln = XmlChild(name='aln', attrname='val')
    children = XmlCollection(
        ControlProperties
    )
