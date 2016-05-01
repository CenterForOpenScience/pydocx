from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.sub import Sub
from pydocx.openxml.shared_math.superscript import Superscript
from pydocx.openxml.shared_math.sub_superscript_properties import SubSuperscriptProperties


class SubSuperscriptFunction(XmlModel):
    XML_TAG = 'sSubSup'

    children = XmlCollection(
        Element,
        Sub,
        Superscript,
        SubSuperscriptProperties
    )
