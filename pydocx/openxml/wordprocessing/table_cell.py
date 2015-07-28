# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.paragraph import Paragraph
from pydocx.openxml.wordprocessing.table_cell_properties import TableCellProperties  # noqa


class TableCell(XmlModel):
    XML_TAG = 'tc'

    properties = XmlChild(type=TableCellProperties)

    children = XmlCollection(
        Paragraph,
        # Table is added in wordprocessing.table
    )
