from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.control_properties import ControlProperties


class SubscriptProperties(XmlModel):
    XML_TAG = 'sSubPr'

    children = XmlCollection(
        ControlProperties
    )
