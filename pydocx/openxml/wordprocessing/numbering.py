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

    def __init__(self, **kwargs):
        super(Numbering, self).__init__(**kwargs)

        self._abstract_nums = {}
        self._nums = {}

        for el in self.elements:
            if isinstance(el, AbstractNum):
                self._abstract_nums[el.abstract_num_id] = el
            elif isinstance(el, NumberingInstance):
                self._nums[el.num_id] = el
            else:
                raise AssertionError(
                    'Unexpected element type {type} encountered'.format(
                        type=el.__class__.__name__,
                    )
                )

    def get_numbering_definition(self, num_id):
        num = self._nums.get(num_id)
        if not num:
            return
        return self._abstract_nums.get(num.abstract_num_id)
