# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.run import Run
from pydocx.openxml.wordprocessing.smart_tag_run import SmartTagRun


class DeletedRun(XmlModel):
    XML_TAG = 'del'

    children = XmlCollection(
        Run,
        SmartTagRun,
        'wordprocessing.DeletedRun',
        # TODO Needs InsertedRun
    )
