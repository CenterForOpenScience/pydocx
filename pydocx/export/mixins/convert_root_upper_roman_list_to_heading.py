# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


class ConvertRootUpperRomanListToHeadingMixin(object):
    def parse_p(self, el, text, stack):
        if text == '':
            return ''

        # TODO This is being done in the base exporter already
        justified_text = self.justification(el, text)

        heading_style_name = self.pre_processor.heading_level(el)

        if heading_style_name:
            return self.heading(
                text=justified_text,
                heading_style_name=heading_style_name,
            )

        return super(ConvertRootUpperRomanListToHeadingMixin, self).parse_p(
            el,
            text,
            stack,
        )
