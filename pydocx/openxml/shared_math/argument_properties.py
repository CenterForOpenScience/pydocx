from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.argument_size import ArgumentSize


class ArgumentProperties(XmlModel):
    XML_TAG = 'argPr'
    children = XmlCollection(
        ArgumentSize
    )
