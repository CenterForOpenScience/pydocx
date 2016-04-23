from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run


class Subscript(XmlModel):
    XML_TAG = 'nary'
    children = XmlCollection(
        Run
    )
