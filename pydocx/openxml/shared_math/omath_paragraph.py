from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.omath import OMath
from pydocx.openxml.shared_math.omath_paragraph_properties import OMathParagraphProperties


class OMathParagraph(XmlModel):

    XML_TAG = 'mathPara'

    children = XmlCollection(
        OMath,
        OMathParagraphProperties
    )
