# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.wordprocessing.sdt_content_run import SdtContentRun


class SdtRun(XmlModel):
    XML_TAG = 'sdt'

    content = XmlChild(type=SdtContentRun)
