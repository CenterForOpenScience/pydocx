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

    @classmethod
    def attributes_list(cls, obj):
        if obj:
            return obj.level_id, obj.num_id

    def __eq__(self, other):
        return self.attributes_list(self) == self.attributes_list(other)

    def __ne__(self, other):
        return not self == other
