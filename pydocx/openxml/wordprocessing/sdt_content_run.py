# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.hyperlink import Hyperlink
from pydocx.openxml.wordprocessing.run import Run
from pydocx.openxml.wordprocessing.smart_tag_run import SmartTagRun
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun


class SdtContentRun(XmlModel):
    XML_TAG = 'sdtContent'

    children = XmlCollection(
        Run,
        Hyperlink,
        SmartTagRun,
        InsertedRun,
        DeletedRun,
        # SdtRun,
    )
