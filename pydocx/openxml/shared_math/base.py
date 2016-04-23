from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run


class Base(XmlModel):
    XML_TAG = 'e'

    children = XmlCollection(
        Run
    )
