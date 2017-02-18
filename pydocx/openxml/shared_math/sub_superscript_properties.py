from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.align_scripts import AlignScripts
from pydocx.openxml.shared_math.control_properties import ControlProperties


class SubSuperscriptProperties(XmlModel):
    XML_TAG = 'sSubSupPr'

    children = XmlCollection(
        AlignScripts,
        ControlProperties
    )
