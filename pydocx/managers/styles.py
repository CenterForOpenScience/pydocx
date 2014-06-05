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

    def get_style(self, style_type, style_id):
        visited_styles = set()
        visited_styles.add(style_id)

        styles = self.styles.get_styles_by_type(style_type)
        base_style = styles.get(style_id)

        style_stack = [base_style]

        # Build up the stack of styles to merge together
        current_style = base_style
        while current_style:
            if not current_style.parent_style:
                # The current style doesn't have a parent style
                break
            if current_style.parent_style in visited_styles:
                # Loop detected
                break
            style = styles.get(current_style.parent_style)
            if not style:
                # Style doesn't exist
                break
            visited_styles.add(style.style_id)
            style_stack.append(style)
            current_style = style

        run_properties = {}
        for style in reversed(style_stack):
            if style and style.run_properties:
                run_properties.update(dict(style.run_properties.items()))
        return run_properties

    def resolve_properties_for_element(self, element):
        properties_dict = {}
        properties = self.properties_for_elements.get(element)
        style_type = self.get_style_type_for_element(element)
        if properties and style_type:
            if properties.parent_style:
                run_properties_dict = self.get_style(
                    style_type,
                    properties.parent_style,
                )
                properties_dict.update(run_properties_dict)
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
