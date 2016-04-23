from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run
from pydocx.openxml.shared_math.delimiter_function import DelimiterFunction
from pydocx.openxml.shared_math.nary_operator_function import NaryOperatorFunction


class OMath(XmlModel):

    XML_TAG = 'oMath'
    children = XmlCollection(
        DelimiterFunction,
        NaryOperatorFunction,
        Run
    )
