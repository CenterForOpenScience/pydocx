from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.base import Base
from pydocx.openxml.shared_math.nary_properties import NaryProperties
from pydocx.openxml.shared_math.subscript import Subscript
from pydocx.openxml.shared_math.superscript import Superscript


class NaryOperatorFunction(XmlModel):
    XML_TAG = 'nary'
    children = XmlCollection(
        Base,
        NaryProperties,
        Subscript,
        Superscript
    )
