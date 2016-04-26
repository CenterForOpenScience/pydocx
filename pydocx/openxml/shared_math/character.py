from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel


class Character(XmlModel):
    """
    Can be a accent character,
    Group character or
    n-ary operator character
    """

    XML_TAG = 'chr'
