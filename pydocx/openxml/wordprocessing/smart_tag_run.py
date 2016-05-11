# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class SmartTagRun(XmlModel):
    XML_TAG = 'smartTag'

    children = XmlCollection(
        'wordprocessing.Run',
        'wordprocessing.SmartTagRun',
    )
