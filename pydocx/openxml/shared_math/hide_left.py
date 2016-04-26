from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class HideLeft(XmlModel):

    XML_TAG = 'hideLeft'
    children = XmlCollection()
