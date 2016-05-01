from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.phantom_properties import PhantomProperties


class PhantomFunction(XmlModel):

    XML_TAG = 'phant'

    children = XmlCollection(
        Element,
        PhantomProperties
    )
