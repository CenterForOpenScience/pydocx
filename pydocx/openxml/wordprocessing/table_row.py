# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.table_cell import TableCell


class TableRow(XmlModel):
    XML_TAG = 'tr'

    cells = XmlCollection(
        TableCell,
    )
