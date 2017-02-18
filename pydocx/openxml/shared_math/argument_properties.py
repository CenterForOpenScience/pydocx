from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.shared_math.argument_size import ArgumentSize


class ArgumentProperties(XmlModel):
    XML_TAG = 'argPr'

    arg_sz = XmlChild(type=ArgumentSize, attrname='val')
