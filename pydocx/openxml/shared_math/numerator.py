from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.delimiter_function import DelimiterFunction
from pydocx.openxml.shared_math.superscript_function import SuperscriptFunction


class Numerator(XmlModel):
    XML_TAG = 'num'
    children = XmlCollection(
        DelimiterFunction,
        SuperscriptFunction
    )
