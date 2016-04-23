from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class NaryProperties(XmlModel):

    chr = XmlChild(name='chr', attrname='val')
