# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute, XmlCollection
from pydocx.openxml.wordprocessing.level import Level


class AbstractNum(XmlModel):
    XML_TAG = 'abstractNum'

    abstract_num_id = XmlAttribute(name='abstractNumId')
    name = XmlChild(attrname='val')

    levels = XmlCollection(Level)

    def __init__(self, **kwargs):
        super(AbstractNum, self).__init__(**kwargs)

        self._levels = {}

        for level in self.levels:
            self._levels[level.level_id] = level

    def get_level(self, level_id):
        return self._levels.get(level_id)

    def get_indentation_between_levels(self):
        """
        Depending on the word version we may get a different default indentation between
        levels. For this we will only check first 2 levels as the other follow the same step.
        """

        try:
            lvl0_ind = self.levels[0].paragraph_properties.to_int('indentation_left',
                                                                  default=0)
            lvl1_ind = self.levels[1].paragraph_properties.to_int('indentation_left',
                                                                  default=0)
            ind_step = lvl1_ind - lvl0_ind
        except IndexError:
            ind_step = 720  # default one

        return ind_step
