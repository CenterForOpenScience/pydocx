from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.run_properties import RunProperties


class ControlProperties(XmlModel):
    XML_TAG = 'ctrlPr'

    children = XmlCollection(
        DeletedRun,
        InsertedRun,
        RunProperties
    )
