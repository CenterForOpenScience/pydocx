from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.base import Base
from pydocx.openxml.shared_math.superscript import Superscript


class SuperscriptFunction(XmlModel):
    XML_TAG = 'sSup'
    children = XmlCollection(
        Base,
        Superscript
    )
