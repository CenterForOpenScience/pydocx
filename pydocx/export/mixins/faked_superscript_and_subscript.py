# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


class FakedSuperscriptAndSubscriptExportMixin(object):
    def get_run_styles_to_apply(self, run):
        # a run is a faked subscript/superscript if the local size is smaller,
        # and the position is raised or lower
        next_in_line = super(FakedSuperscriptAndSubscriptExportMixin, self)
        styles = next_in_line.get_run_styles_to_apply(run)

        inherited_properties = run.inherited_properties
        effective_properties = run.effective_properties

        def could_be_a_faked_sub_or_superscript():
            if effective_properties is None:
                return False
            if effective_properties.size is None:
                return False
            if inherited_properties is None:
                return False
            if inherited_properties.size is None:
                return False
            if run.properties is None:
                return False
            if not run.properties.size:
                return False
            if effective_properties.is_superscript():
                return False
            if effective_properties.is_subscript():
                return False
            if run.properties.size >= inherited_properties.size:
                return False
            return True

        if could_be_a_faked_sub_or_superscript():
            vertical_position = run.properties.position
            if vertical_position > 0:
                yield self.export_run_property_vertical_align_superscript
            elif vertical_position < 0:
                yield self.export_run_property_vertical_align_subscript

        for style in styles:
            yield style
