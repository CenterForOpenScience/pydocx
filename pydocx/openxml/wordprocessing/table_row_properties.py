# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class TableRowProperties(XmlModel):
    XML_TAG = 'trPr'

    # The presence of <w:hidden/> means the row is hidden.
    # XmlChild without attrname returns the raw element if found,
    # or None (default) if absent — so bool(hidden) works directly.
    hidden = XmlChild(name='hidden')