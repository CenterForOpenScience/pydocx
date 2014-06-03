from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


class Style(object):
    def __init__(self, style_id, style_type, name):
        self.style_id = style_id
        self.style_type = style_type
        self.name = name

    @staticmethod
    def load(element):
        style_type = element.attrib.get('type', 'paragraph')
        style_id = element.attrib.get('styleId', '')
        name = ''
        for child in element:
            if child.tag == 'name' and not name:
                name = child.attrib.get('val', '')
        return Style(
            style_id=style_id,
            style_type=style_type,
            name=name,
        )


class Styles(object):
    def __init__(self, styles):
        self.styles = styles

    @staticmethod
    def load(root):
        styles = [
            Style.load(element=element)
            for element in root
            if element.tag == 'style'
        ]
        return Styles(styles)
