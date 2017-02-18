from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.delimiter_function import DelimiterFunction
from pydocx.openxml.wordprocessing.run import Run


class Superscript(XmlModel):
    XML_TAG = 'nary'
    children = XmlCollection(
        DelimiterFunction,
        Run
    )
