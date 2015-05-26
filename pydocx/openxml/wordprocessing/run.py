# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.openxml.wordprocessing.br import Break
from pydocx.openxml.wordprocessing.no_break_hyphen import NoBreakHyphen
from pydocx.openxml.wordprocessing.text import Text


class Run(XmlModel):
    XML_TAG = 'r'

    properties = XmlChild(type=RunProperties)

    children = XmlCollection(
        Break,
        NoBreakHyphen,
        Text,
    )
