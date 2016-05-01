from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.justification import Justification


class OMathParagraphProperties(XmlModel):

    XML_TAG = 'mathParaPr'

    children = XmlCollection(
        Justification
    )
