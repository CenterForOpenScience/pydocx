# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlAttribute
from pydocx.openxml.wordprocessing.paragraph import Paragraph
from pydocx.openxml.wordprocessing.table import Table
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun


class Footnote(XmlModel):
    XML_TAG = 'footnote'

    footnote_id = XmlAttribute(name='id')

    children = XmlCollection(
        Paragraph,
        Table,
        InsertedRun,
        DeletedRun,
    )
