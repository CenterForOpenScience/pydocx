from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import defaultdict

from pydocx.types import OnOff


class RunProperties(object):
    def __init__(self, bold=False):
        self.bold = bool(OnOff(bold))

    @staticmethod
    def load(element):
        bold = False
        for child in element:
            if child.tag == 'b' and not bold:
                bold = child.attrib.get('val', '')
        return RunProperties(
            bold=bold,
        )


class Style(object):
    def __init__(self, style_id, style_type, name, run_properties):
        self.style_id = style_id
        self.style_type = style_type
        self.name = name
        self.run_properties = run_properties

    @staticmethod
    def load(element):
        style_type = element.attrib.get('type', 'paragraph')
        style_id = element.attrib.get('styleId', '')
        name = ''
        run_properties = None
        for child in element:
            if child.tag == 'name' and not name:
                name = child.attrib.get('val', '')
            if child.tag == 'rPr' and not run_properties:
                run_properties = RunProperties.load(child)
        return Style(
            style_id=style_id,
            style_type=style_type,
            name=name,
            run_properties=run_properties,
        )


class Styles(object):
    def __init__(self, styles):
        self.styles = styles
        styles_by_type = defaultdict(dict)
        for style in self.styles:
            styles_by_type[style.style_type][style.style_id] = style
        self.styles_by_type = dict(styles_by_type)

    @staticmethod
    def load(root):
        styles = [
            Style.load(element=element)
            for element in root
            if element.tag == 'style'
        ]
        return Styles(styles)

    def get_styles_by_type(self, style_type):
        return self.styles_by_type.get(style_type, {})
