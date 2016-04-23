from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run


class Denominator(XmlModel):
    XML_TAG = 'den'
    children = XmlCollection(
        Run
    )
