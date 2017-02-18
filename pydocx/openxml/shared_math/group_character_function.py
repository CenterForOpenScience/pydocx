from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.group_character_properties import GroupCharacterProperties


class GroupCharacterFunction(XmlModel):
    XML_TAG = 'groupChr'

    children = XmlCollection(
        Element,
        GroupCharacterProperties
    )
