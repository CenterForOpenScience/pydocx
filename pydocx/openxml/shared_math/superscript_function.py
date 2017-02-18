from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.superscript import Superscript
from pydocx.openxml.shared_math.superscript_properties import SuperscriptProperties


class SuperscriptFunction(XmlModel):
    XML_TAG = 'sSup'

    children = XmlCollection(
        Element,
        Superscript,
        SuperscriptProperties
    )
