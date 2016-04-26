from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.hide_degree import HideDegree


class RadicalProperties(XmlModel):
    XML_TAG = 'ctrlPr'
    children = XmlCollection(
        ControlProperties,
        HideDegree
    )
