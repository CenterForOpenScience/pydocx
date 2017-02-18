from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.pre_sub_superscript_properties import (
    PreSubSuperscriptProperties
)
from pydocx.openxml.shared_math.sub import Sub
from pydocx.openxml.shared_math.superscript import Superscript


class PreSubSuperscriptFunction(XmlModel):
    XML_TAG = 'sPre'

    children = XmlCollection(
        Element,
        PreSubSuperscriptProperties,
        Sub,
        Superscript
    )
