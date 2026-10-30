# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.open_xml_part import OpenXmlPart
from pydocx.openxml.wordprocessing import Styles


class StyleDefinitionsPart(OpenXmlPart):
    '''
    Represents style definitions within a Word document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.styledefinitionspart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'styles',
    ])

    def __init__(self, *args, **kwargs):
        super(StyleDefinitionsPart, self).__init__(*args, **kwargs)
        self._styles = None

    @property
    def styles(self):
        if self._styles:
            return self._styles
        self._styles = Styles.load(self.root_element, container=self)
        return self._styles

    def get_style_chain_stack(self, style_type, style_id):
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
        styles = self.styles.get_styles_by_type(style_type)
        styles_to_apply = {}

        def yield_styles_parent_stack(base_style):
            if base_style:
                yield base_style

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
                yield style
                current_style = style

        if not style_id:
            # In this case we need to check the default defined styles
            styles_to_apply = self.styles.get_default_styles_by_type(style_type)
        else:
            styles_to_apply[style_id] = styles.get(style_id)

        for style_id, style in styles_to_apply.items():
            visited_styles.add(style_id)
            for s in yield_styles_parent_stack(style):
                yield s
