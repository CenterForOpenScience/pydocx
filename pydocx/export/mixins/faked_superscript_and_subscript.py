# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import copy


class FakedSuperscriptAndSubscriptExportMixin(object):
    def parse_r_determine_applicable_styles(self, el, stack):
        next_in_line = super(FakedSuperscriptAndSubscriptExportMixin, self)
        styles = next_in_line.parse_r_determine_applicable_styles(el, stack)

        properties = self.document.main_document_part.style_definitions_part.get_resolved_properties_for_element(  # noqa
            el,
            stack,
        )

        def get_properties_with_no_font_size():
            # Only set paragraph_properties if properties has a size.
            if not properties.size:
                return
            copied_el = copy.deepcopy(el)
            rpr = copied_el.find('./rPr')
            if rpr is None:
                return

            size_tag = rpr.find('./sz')
            if size_tag is None:
                return

            rpr.remove(size_tag)

            return self.document.main_document_part.style_definitions_part.get_resolved_properties_for_element(  # noqa
                copied_el,
                stack,
            )

        paragraph_properties = get_properties_with_no_font_size()

        # If paragraph_properties is None then the size was not set
        # (meaning it can't be bigger or smaller than the default for the
        # paragraph, so early exit.
        if paragraph_properties is None:
            return styles

        if paragraph_properties.size is None:
            return styles

        if paragraph_properties.size < properties.size:
            return styles

        if not properties.position:
            return styles

        if self.subscript in styles:
            return styles

        if self.superscript in styles:
            return styles

        if properties.position > 0:
            styles.append(self.superscript)
        else:
            styles.append(self.subscript)

        return styles
