# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.wordprocessing.abstract_num import AbstractNum
from pydocx.openxml.wordprocessing.numbering_instance import NumberingInstance


class Numbering(XmlModel):
    XML_TAG = 'numbering'

    elements = XmlCollection(AbstractNum, NumberingInstance)
