# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.wordprocessing.numbering_properties import NumberingProperties  # noqa


class ParagraphProperties(XmlModel):
    XML_TAG = 'pPr'

    parent_style = XmlChild(name='pStyle', attrname='val')
    numbering_properties = XmlChild(type=NumberingProperties)
    justification = XmlChild(name='jc', attrname='val')
    # TODO ind can appear multiple times. Need to merge them in document order
    # This probably means other elements can appear multiple times

    # TODO Left/right is for traditional conformance. Need to handle start/end
    # for strict conformance
    indentation_left = XmlChild(name='ind', attrname='left')
    indentation_right = XmlChild(name='ind', attrname='right')
    indentation_first_line = XmlChild(name='ind', attrname='firstLine')
    indentation_hanging = XmlChild(name='ind', attrname='hanging')
