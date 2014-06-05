from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from pydocx.models.styles import (
    Styles,
)


class StylesManager(object):
    def __init__(self, style_definitions_part):
        self.style_definitions_part = style_definitions_part
        if style_definitions_part:
            self.styles = Styles.load(style_definitions_part.root_element)
        else:
            self.styles = Styles()
