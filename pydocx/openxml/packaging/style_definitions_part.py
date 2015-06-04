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
        visited_styles.add(style_id)

        styles = self.styles.get_styles_by_type(style_type)
        base_style = styles.get(style_id)

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
