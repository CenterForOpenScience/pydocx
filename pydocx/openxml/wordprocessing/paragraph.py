# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.paragraph_properties import ParagraphProperties  # noqa
from pydocx.openxml.wordprocessing.run import Run


class Paragraph(XmlModel):
    XML_TAG = 'p'

    properties = XmlChild(type=ParagraphProperties)

    children = XmlCollection(
        Run,
    )
