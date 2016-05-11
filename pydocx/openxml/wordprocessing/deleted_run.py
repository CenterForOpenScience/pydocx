# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection


class DeletedRun(XmlModel):
    XML_TAG = 'del'

    children = XmlCollection(
        'wordprocessing.Run',
        'wordprocessing.SmartTagRun',
        'wordprocessing.DeletedRun',
        # TODO Needs InsertedRun
    )
