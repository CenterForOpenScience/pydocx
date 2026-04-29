# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlCollection
from pydocx.openxml.wordprocessing.table_cell import TableCell
from pydocx.openxml.wordprocessing.table_row_properties import TableRowProperties  # NEW


class TableRow(XmlModel):
    XML_TAG = 'tr'

    # NEW: wire in the trPr properties element
    properties = XmlChild(type=TableRowProperties)

    cells = XmlCollection(TableCell)

    @property
    def is_hidden(self):
        """Return True if this row has <w:trPr><w:hidden/></w:trPr>."""
        return self.properties is not None and self.properties.hidden is not None