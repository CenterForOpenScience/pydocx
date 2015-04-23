# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute, XmlCollection
from pydocx.openxml.wordprocessing.level import Level


class AbstractNum(XmlModel):
    abstract_num_id = XmlAttribute(name='abstractNumId')
    name = XmlChild(attrname='val')

    levels = XmlCollection({
        'lvl': Level,
    })
