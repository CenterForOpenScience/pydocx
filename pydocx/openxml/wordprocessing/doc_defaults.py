# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild
from pydocx.openxml.wordprocessing.paragraph_properties import ParagraphProperties
from pydocx.openxml.wordprocessing.run_properties import RunProperties


class ParagraphStyleDefaults(XmlModel):
    XML_TAG = 'pPrDefault'

    properties = XmlChild(type=ParagraphProperties)


class RunStyleDefaults(XmlModel):
    XML_TAG = 'rPrDefault'

    properties = XmlChild(type=RunProperties)


class DocDefaults(XmlModel):
    XML_TAG = 'docDefaults'

    paragraph = XmlChild(type=ParagraphStyleDefaults)
    run = XmlChild(type=RunStyleDefaults)
