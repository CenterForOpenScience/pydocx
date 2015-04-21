# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict

from pydocx.openxml.wordprocessing.style import Style


class Styles(object):
    def __init__(self, styles=None):
        if styles is None:
            styles = []
        self.styles = list(styles)
        styles_by_type = defaultdict(dict)
        for style in self.styles:
            styles_by_type[style.style_type][style.style_id] = style
        self.styles_by_type = dict(styles_by_type)

    @staticmethod
    def load(root):
        styles = []
        for element in root:
            if element.tag == 'style':
                style = Style.load(element)
                styles.append(style)
        return Styles(styles)

    def get_styles_by_type(self, style_type):
        return self.styles_by_type.get(style_type, {})
