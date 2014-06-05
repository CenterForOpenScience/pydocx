from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from pydocx.models.styles import (
    RunProperties,
    Styles,
)


class StylesManager(object):
    def __init__(self, style_definitions_part=None):
        self.style_definitions_part = style_definitions_part
        if style_definitions_part:
            self.styles = Styles.load(style_definitions_part.root_element)
        else:
            self.styles = Styles()
        self.properties_for_elements = {}
        self.properties_cache = {}
        self.tag_to_style_type_map = {
            'p': 'paragraph',
            'r': 'character',
        }

    def get_style_type_for_element(self, element):
        return self.tag_to_style_type_map.get(element.tag)

    def save_properties_for_element(self, element, properties):
        self.properties_for_elements[element] = properties

    def resolve_properties_for_element(self, element):
        properties_dict = {}
        properties = self.properties_for_elements.get(element)
        style_type = self.get_style_type_for_element(element)
        if properties and style_type:
            if properties.parent_style:
                styles = self.styles.get_styles_by_type(style_type)
                style = styles.get(properties.parent_style)
                if style and style.run_properties:
                    properties_dict.update(dict(style.run_properties.items()))
            if style_type == 'character':
                properties_dict.update(dict(properties.items()))
        return properties_dict

    def get_resolved_properties_for_element(self, el, stack):
        properties = {}

        for item in stack:
            element = item['element']
            properties.update(self.resolve_properties_for_element(element))

        properties.update(
            self.resolve_properties_for_element(el),
        )

        run_properties = RunProperties(**properties)
        return run_properties
