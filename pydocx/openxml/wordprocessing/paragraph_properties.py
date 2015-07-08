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

    @property
    def start_margin_position(self):
        # Regarding indentation,
        #   position = left - hanging
        #   position = left + firstLine (only if hanging isn't specified)
        # 17.3.1.12 - The firstLine and hanging attributes are mutually
        # exclusive, if both are specified, then the firstLine value is
        # ignored.
        start_margin = 0
        if self.indentation_left:
            start_margin += int(self.indentation_left)
        if self.indentation_hanging:
            start_margin -= int(self.indentation_hanging)
        elif self.indentation_first_line:
            start_margin += int(self.indentation_first_line)
        if start_margin:
            return start_margin
        return 0
