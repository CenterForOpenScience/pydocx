# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlCollection
from pydocx.openxml.wordprocessing.paragraph import Paragraph
from pydocx.openxml.wordprocessing.table import Table
from pydocx.openxml.wordprocessing.section_properties import SectionProperties
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun
from pydocx.openxml.wordprocessing.sdt_block import SdtBlock


class Body(XmlModel):
    XML_TAG = 'body'

    children = XmlCollection(
        Paragraph,
        Table,
        InsertedRun,
        DeletedRun,
        SdtBlock,
    )

    final_section_properties = XmlChild(type=SectionProperties)
