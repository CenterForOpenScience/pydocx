# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.wordprocessing.sdt_content_block import SdtContentBlock


class SdtBlock(XmlModel):
    XML_TAG = 'sdt'

    content = XmlChild(type=SdtContentBlock)
