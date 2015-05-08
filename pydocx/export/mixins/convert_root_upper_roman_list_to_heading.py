# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging import NumberingDefinitionsPart


class ConvertRootUpperRomanListToHeadingMixin(object):
    HEADING_LEVEL = 'heading 2'

    def _is_element_a_root_level_upper_roman_list_item(self, el):
        numbering = self.numbering_definitions_part.numbering

        properties = self.style_definitions_part.properties_for_elements.get(el)  # noqa
        num_props = properties.numbering_properties
        if not num_props:
            return False

        if not num_props.is_root_level():
            return False

        num_definition = numbering.get_numbering_definition(num_id=num_props.num_id)  # noqa
        if not num_definition:
            return False

        level = num_definition.get_level(level_id=num_props.level_id)
        if not level:
            return False

        return level.num_format == NumberingDefinitionsPart.NUM_FORMAT_UPPER_ROMAN  # noqa

    def parse_p(self, el, text, stack):
        if text == '':
            return ''

        if self._is_element_a_root_level_upper_roman_list_item(el):
            # TODO justification is being done in the base exporter
            justified_text = self.justification(el, text)
            return self.heading(
                text=justified_text,
                heading_style_name=self.HEADING_LEVEL,
            )

        return super(ConvertRootUpperRomanListToHeadingMixin, self).parse_p(
            el,
            text,
            stack,
        )
