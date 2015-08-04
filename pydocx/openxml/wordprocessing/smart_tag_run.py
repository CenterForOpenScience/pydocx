# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run


class SmartTagRun(XmlModel):
    XML_TAG = 'smartTag'

    children = XmlCollection(
        Run,
    )

SmartTagRun.children.types.add(SmartTagRun)
