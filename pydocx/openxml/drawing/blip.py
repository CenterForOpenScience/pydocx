# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlAttribute


class Blip(XmlModel):
    XML_TAG = 'blip'

    embedded_picture_id = XmlAttribute(name='embed')
    linked_picture_id = XmlAttribute(name='link')
