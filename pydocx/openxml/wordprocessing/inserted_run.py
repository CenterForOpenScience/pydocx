# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class InsertedRun(XmlModel):
    XML_TAG = 'ins'

    children = XmlCollection(
        'wordprocessing.Run',
        'wordprocessing.SmartTagRun',
        'wordprocessing.InsertedRun',
        # TODO Needs DeletedRun
    )
