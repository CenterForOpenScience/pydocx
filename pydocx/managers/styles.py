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

    def save_properties_for_element(self, element, properties):
        self.properties_for_elements[element] = properties

    def get_resolved_properties_for_element(self, el, stack):
        parent_paragraph = stack[-1]['element']
        parent_paragraph_properties = self.properties_for_elements.get(
            parent_paragraph,
        )

        properties = {}
        if parent_paragraph_properties and \
                parent_paragraph_properties.parent_style:
            paragraph_styles = self.styles.get_styles_by_type('paragraph')
            parent_paragraph_style = paragraph_styles.get(
                parent_paragraph_properties.parent_style,
            )
            if parent_paragraph_style and \
                    parent_paragraph_style.run_properties:
                properties = dict(
                    parent_paragraph_style.run_properties.items()
                )

        direct_properties = self.properties_for_elements.get(el)
        if direct_properties:
            if direct_properties.parent_style:
                character_styles = self.styles.get_styles_by_type('character')
                parent_character_style = character_styles.get(
                    direct_properties.parent_style,
                )
                if parent_character_style and \
                        parent_character_style.run_properties:
                    properties.update(
                        dict(parent_character_style.run_properties.items())
                    )

            properties.update(dict(direct_properties.items()))

        run_properties = RunProperties(**properties)
        return run_properties
