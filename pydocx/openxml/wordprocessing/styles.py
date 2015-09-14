# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict

from pydocx.models import XmlCollection, XmlModel
from pydocx.openxml.wordprocessing.style import Style


class Styles(XmlModel):
    XML_TAG = 'styles'

    styles = XmlCollection(Style)

    def __init__(self, styles=None, *args, **kwargs):
        super(Styles, self).__init__(styles=styles, *args, **kwargs)

        styles_by_type = defaultdict(dict)
        for style in self.styles:
            styles_by_type[style.style_type][style.style_id] = style
        self.styles_by_type = dict(styles_by_type)

    def get_styles_by_type(self, style_type):
        return self.styles_by_type.get(style_type, {})
