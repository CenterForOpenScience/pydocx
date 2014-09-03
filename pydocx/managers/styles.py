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
    '''
    A class that is responsible for managing per-element direct formatting
    properties, and resolving style chain references defined within that
    formatting.
    '''
    def __init__(self, style_definitions_part=None):
        self.style_definitions_part = style_definitions_part
        if style_definitions_part:
            self.styles = Styles.load(style_definitions_part.root_element)
        else:
            self.styles = Styles()
        self.properties_for_elements = {}
        self.tag_to_style_type_map = {
            'p': 'paragraph',
            'r': 'character',
        }

    def save_properties_for_element(self, element, properties):
        self.properties_for_elements[element] = properties

    def _get_style_chain_stack(self, style_type, style_id):
        '''
        Given a style_type and style_id, return the hierarchy of styles ordered
        ascending.

        For example, given the following style specification:

        styleA -> styleB
        styleB -> styleC

        If this method is called using style_id=styleA, the result will be:

        styleA
        styleB
        styleC
        '''
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
        return style_stack

    def _get_merged_style_chain(self, style_type, style_id):
        '''
        Given a style type and style id, calculate the style chain stack and
        return the merged properties between each style in the stack.
        '''
        style_stack = self._get_style_chain_stack(style_type, style_id)

        run_properties = {}
        for style in reversed(style_stack):
            if style and style.run_properties:
                run_properties.update(dict(style.run_properties.items()))
        return run_properties

    def _resolve_properties_for_element(self, element):
        '''
        Given an element return the "resolved" properties for that element.

        A resolved property set includes the element's direct properties, plus
        any globally defined styles that the element may reference.

        For example, given the following direct formatting:

        bold=True
        style="Normal"

        The returned result would be a merge between the properties defined by
        the style chain defined by "Normal" and the direct formatting specified
        by the element, with the direct formatting taking precedence.
        '''
        properties_dict = {}
        properties = self.properties_for_elements.get(element)
        style_type = self.tag_to_style_type_map.get(element.tag)
        if properties and style_type:
            if properties.parent_style:
                run_properties_dict = self._get_merged_style_chain(
                    style_type,
                    properties.parent_style,
                )
                properties_dict.update(run_properties_dict)
            if style_type == 'character':
                properties_dict.update(dict(properties.items()))
        return properties_dict

    def get_resolved_properties_for_element(self, el, stack):
        '''
        Given an element and a stack of ancestors, calculate the properties at
        each level, merge the properties, and return the result.
        '''
        properties = {}

        for item in stack:
            element = item['element']
            properties.update(self._resolve_properties_for_element(element))

        properties.update(self._resolve_properties_for_element(el))
        run_properties = RunProperties(**properties)
        return run_properties
