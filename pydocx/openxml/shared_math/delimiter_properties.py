from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class DelimiterProperties(XmlModel):
    XML_TAG = 'dPr'
    beg_chr = XmlChild(name='begChr', attrname='val')
    end_chr = XmlChild(name='endChr', attrname='val')
