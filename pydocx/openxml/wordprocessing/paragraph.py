# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.bookmark import Bookmark
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun
from pydocx.openxml.wordprocessing.hyperlink import Hyperlink
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.paragraph_properties import ParagraphProperties  # noqa
from pydocx.openxml.wordprocessing.run import Run
from pydocx.openxml.wordprocessing.sdt_run import SdtRun
from pydocx.openxml.wordprocessing.simple_field import SimpleField
from pydocx.openxml.wordprocessing.smart_tag_run import SmartTagRun
from pydocx.openxml.wordprocessing.tab_char import TabChar
from pydocx.openxml.wordprocessing.text import Text
from pydocx.util.memoize import memoized


class Paragraph(XmlModel):
    XML_TAG = 'p'

    properties = XmlChild(type=ParagraphProperties)

    children = XmlCollection(
        Run,
        Hyperlink,
        SmartTagRun,
        InsertedRun,
        DeletedRun,
        SdtRun,
        SimpleField,
        Bookmark
    )

    @property
    def is_empty(self):
        if not self.children:
            return True

        # we may have cases when a paragraph has a Bookmark with name '_GoBack'
        # and we should treat it as empty paragraph
        if len(self.children) == 1:
            first_child = self.children[0]
            if isinstance(first_child, Bookmark) and \
                    first_child.name in ('_GoBack',):
                return True
            # We can have cases when only run properties are defined and no text
            elif not getattr(first_child, "children", None):
                return True
        return False

    def _get_properties_inherited_from_parent_table(self):
        from pydocx.openxml.wordprocessing.table import Table

        inherited_properties = {}

        parent_table = self.get_first_ancestor(Table)
        if parent_table:
            style_stack = parent_table.get_style_chain_stack()
            for style in reversed(list(style_stack)):
                if style.paragraph_properties:
                    inherited_properties.update(
                        dict(style.paragraph_properties.fields),
                    )
        return inherited_properties

    def _get_inherited_properties_from_parent_style(self):
        inherited_properties = {}
        style_stack = self.get_style_chain_stack()
        for style in reversed(list(style_stack)):
            if style.paragraph_properties:
                inherited_properties.update(
                    dict(style.paragraph_properties.fields),
                )
        return inherited_properties

    @property
    def inherited_properties(self):
        properties = {}

        if self.default_doc_styles and \
                getattr(self.default_doc_styles.paragraph, 'properties'):
            properties.update(
                dict(self.default_doc_styles.paragraph.properties.fields),
            )
        properties.update(
            self._get_inherited_properties_from_parent_style(),
        )
        # Tables can also define custom paragraph pr
        properties.update(
            self._get_properties_inherited_from_parent_table(),
        )

        # TODO When enable this make sure that you check the paragraph margins logic
        # numbering_level = self.get_numbering_level()
        # if numbering_level and numbering_level.paragraph_properties:
        #     properties.update(
        #         dict(numbering_level.paragraph_properties.fields),
        #     )

        return ParagraphProperties(**properties)

    @property
    @memoized
    def effective_properties(self):
        inherited_properties = self.inherited_properties
        effective_properties = {}
        effective_properties.update(dict(inherited_properties.fields))
        if self.properties:
            effective_properties.update(dict(self.properties.fields))
        return ParagraphProperties(**effective_properties)

    @property
    def numbering_definition(self):
        return self.get_numbering_definition()

    def has_structured_document_parent(self):
        from pydocx.openxml.wordprocessing import SdtBlock
        return self.has_ancestor(SdtBlock)

    def get_style_chain_stack(self):
        # Even if parent style is not defined we still need to check the default style
        # properties applied
        parent_style = getattr(self.properties, 'parent_style', None)

        # TODO the getattr is necessary because of footnotes. From the context
        # of a footnote, a paragraph's container is the footnote part, which
        # doesn't have access to the style_definitions_part
        part = getattr(self.container, 'style_definitions_part', None)
        if part:
            style_stack = part.get_style_chain_stack('paragraph', parent_style)
            for result in style_stack:
                yield result

    @property
    def heading_style(self):
        if hasattr(self, '_heading_style'):
            return getattr(self, '_heading_style')
        style_stack = self.get_style_chain_stack()
        heading_style = None
        for style in style_stack:
            if style.is_a_heading():
                heading_style = style
                break
        self.heading_style = heading_style
        return heading_style

    @heading_style.setter
    def heading_style(self, style):
        self._heading_style = style

    @memoized
    def get_numbering_definition(self):
        # TODO the getattr is necessary because of footnotes. From the context
        # of a footnote, a paragraph's container is the footnote part, which
        # doesn't have access to the numbering_definitions_part
        part = getattr(self.container, 'numbering_definitions_part', None)
        if not part:
            return
        if not self.properties:
            return
        numbering_properties = self.properties.numbering_properties
        if not numbering_properties:
            return
        return part.numbering.get_numbering_definition(
            num_id=numbering_properties.num_id,
        )

    @memoized
    def get_numbering_level(self):
        numbering_definition = self.get_numbering_definition()
        if not numbering_definition:
            return
        if not self.properties:
            return
        numbering_properties = self.properties.numbering_properties
        if not numbering_properties:
            return
        return numbering_definition.get_level(
            level_id=numbering_properties.level_id,
        )

    @property
    def runs(self):
        for p_child in self.children:
            if isinstance(p_child, Run):
                yield p_child

    @property
    def bookmark_name(self):
        for p_child in self.children:
            if isinstance(p_child, Bookmark):
                return p_child.name

    def get_text(self, tab_char=None):
        '''
        Return a string of all of the contained Text nodes concatenated
        together. If `tab_char` is set, then any TabChar encountered will be
        represented in the returned text using the specified string.

        For example:

        Given the following paragraph XML definition:

            <p>
                <r>
                    <t>abc</t>
                </r>
                <r>
                    <t>def</t>
                </r>
            </p>

        `get_text()` will return 'abcdef'
        '''

        text = []
        for run in self.runs:
            for r_child in run.children:
                if isinstance(r_child, Text):
                    if r_child.text:
                        text.append(r_child.text)
                if tab_char and isinstance(r_child, TabChar):
                    text.append(tab_char)
        return ''.join(text)

    def get_number_of_initial_tabs(self):
        '''
        Return the number of initial TabChars.
        '''
        tab_count = 0
        for p_child in self.children:
            if isinstance(p_child, Run):
                for r_child in p_child.children:
                    if isinstance(r_child, TabChar):
                        tab_count += 1
                    else:
                        break
            else:
                break
        return tab_count

    @property
    @memoized
    def has_numbering_properties(self):
        return bool(getattr(self.properties, 'numbering_properties', None))

    @property
    @memoized
    def has_numbering_definition(self):
        return bool(self.numbering_definition)

    def get_indentation(self, indentation, only_level_ind=False):
        '''
        Get specific indentation of the current paragraph. If indentation is
        not present on the paragraph level, get it from the numbering definition.
        '''

        ind = None

        if self.properties:
            if not only_level_ind:
                ind = self.properties.to_int(indentation)
            if ind is None:
                level = self.get_numbering_level()
                ind = level.paragraph_properties.to_int(indentation, default=0)

        return ind

    def get_spacing(self):
        """Get paragraph spacing according to:
                ECMA-376, 3rd Edition (June, 2011),
                Fundamentals and Markup Language Reference § 17.3.1.33.
        """
        results = {
            'line': None,
            'after': None,
            'before': None,
            'contextual_spacing': bool(self.effective_properties.contextual_spacing),
            'parent_style': self.effective_properties.parent_style
        }

        spacing_properties = self.effective_properties.spacing_properties

        if spacing_properties is None:
            return results

        spacing_line = spacing_properties.to_int('line')
        spacing_after = spacing_properties.to_int('after')
        spacing_before = spacing_properties.to_int('before')

        if spacing_line:
            line = float("%.2f" % (spacing_line / 240.0))
            # default line spacing is 1 so no need to add attribute
            if line != 1.0:
                results['line'] = line

        if spacing_after is not None:
            results['after'] = spacing_after

        if spacing_before is not None:
            results['before'] = spacing_before

        return results
