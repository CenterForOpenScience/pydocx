# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild


class NumberingProperties(XmlModel):
    XML_TAG = 'numPr'

    ROOT_LEVEL_ID = '0'

    level_id = XmlChild(name='ilvl', attrname='val')
    num_id = XmlChild(name='numId', attrname='val')

    def is_root_level(self):
        if self.num_id is None or self.level_id is None:
            return False

        return self.level_id == self.ROOT_LEVEL_ID
