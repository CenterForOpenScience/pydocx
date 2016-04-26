from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class HideBottom(XmlModel):

    XML_TAG = 'hideBot'
    children = XmlCollection()
