from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.shared_math.align import Align
from pydocx.openxml.shared_math.brk import Break
from pydocx.openxml.shared_math.differential import Differential
from pydocx.openxml.shared_math.no_break import NoBreak
from pydocx.openxml.shared_math.operator_emulator import OperatorEmulator
from pydocx.openxml.shared_math.control_properties import ControlProperties


class BoxProperties(XmlModel):

    XML_TAG = 'boxPr'
    aln = XmlChild(type=Align, attrname='val')
    brk = XmlChild(type=Break, attrname='val')
    diff = XmlChild(type=Differential, attrname='val')
    no_break = XmlChild(type=NoBreak, attrname='val')
    op_emu = XmlChild(type=OperatorEmulator, attrname='val')
    children = XmlCollection(
        ControlProperties
    )
