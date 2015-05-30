# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.table_cell import TableCell
from pydocx.openxml.wordprocessing.table_row import TableRow


class Table(XmlModel):
    XML_TAG = 'tbl'

    rows = XmlCollection(
        TableRow,
    )


# Python makes defining nested class hierarchies at the global level difficult
TableCell.children.types.add(Table)
