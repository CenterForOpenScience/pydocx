from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel


class BaseJustification(XmlModel):
    XML_TAG = 'baseJc'
