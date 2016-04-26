from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlCollection
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.delimiter_beginning_character import (
    DelimiterBeginningCharacter
)
from pydocx.openxml.shared_math.delimiter_separator_character import (
    DelimiterSeparatorCharacter
)
from pydocx.openxml.shared_math.delimiter_ending_character import DelimiterEndingCharacter
from pydocx.openxml.shared_math.grow import Grow
from pydocx.openxml.shared_math.shape import Shape


class DelimiterProperties(XmlModel):
    XML_TAG = 'dPr'

    beg_chr = XmlChild(type=DelimiterBeginningCharacter, attrname='val')
    sep_chs = XmlChild(type=DelimiterSeparatorCharacter, attrname='val')
    end_chr = XmlChild(type=DelimiterEndingCharacter, attrname='val')
    grow = XmlChild(type=Grow, attrname='val')
    shape = XmlChild(type=Shape, attrname='val')

    children = XmlCollection(
        ControlProperties
    )
