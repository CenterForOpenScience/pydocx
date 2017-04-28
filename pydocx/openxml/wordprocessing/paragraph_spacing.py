# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlAttribute
from pydocx.types import OnOff


class ParagraphSpacing(XmlModel):
    XML_TAG = 'spacing'

    after = XmlAttribute(name='after')
    before = XmlAttribute(name='before')
    line = XmlAttribute(name='line')
    line_rule = XmlAttribute(name='lineRule')
    after_auto_spacing = XmlAttribute(type=OnOff, name='afterAutospacing')

    def to_int(self, attribute, default=None):
        # TODO would be nice if this integer conversion was handled
        # implicitly by the model somehow
        try:
            return int(getattr(self, attribute, default))
        except (ValueError, TypeError):
            return default
