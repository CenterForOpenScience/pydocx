from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.shared_math.character import Character


class NaryProperties(XmlModel):

    chr = XmlChild(type=Character, attrname='val')
