# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from pydocx.export.html_tag import HtmlTag
from pydocx.export.numbering_span import NumberingItem
from pydocx.openxml.wordprocessing import Run, Paragraph, TableCell
from pydocx.util.xml import convert_dictionary_to_style_fragment


class NoBorderAndShadingBuilder(object):
    TAGS = {
        'Paragraph': 'div',
        'Run': 'span'
    }

    def __init__(self, items):
        self.items = items
        self.current_border_item = {}
        self.item = None
        self.prev_item = None

    def export_borders(self, item, results, first_pass=True):
        if results:
            for result in results:
                yield result


class BorderAndShadingBuilder(NoBorderAndShadingBuilder):
    @property
    def item_is_paragraph(self):
        return isinstance(self.item, Paragraph)

    @property
    def item_is_run(self):
        return isinstance(self.item, Run)

    @property
    def item_name(self):
        return self.item.__class__.__name__

    @property
    def tag_name(self):
        return self.TAGS[self.item_name]

    def current_item_is_last_child(self, children, child_type):
        for p_child in reversed(children):
            if isinstance(p_child, child_type):
                return p_child == self.item
        return False

    def is_last_item(self):
        if self.item_is_paragraph:
            if isinstance(self.item.parent, (TableCell, NumberingItem)):
                return self.current_item_is_last_child(
                    self.item.parent.children, Paragraph)
            elif self.item == self.items[-1]:
                return True
        elif self.item_is_run:
            # Check if current item is the last Run item from paragraph children
            return self.current_item_is_last_child(self.item.parent.children, Run)

        return False

    def close_tag(self):
        self.current_border_item[self.item_name] = None
        return HtmlTag(self.tag_name, closed=True)

    def get_next_item(self):
        next_item = None

        try:
            cur_item_idx = self.items.index(self.item)
            if cur_item_idx < len(self.items) - 1:
                next_item = self.items[cur_item_idx + 1]
        except ValueError:
            pass

        return next_item

    def is_next_paragraph_listing(self):
        """Check if current item is not listing but next one is listing"""

        if not self.item_is_paragraph:
            return False

        next_item = self.get_next_item()
        if next_item:
            if not self.item.has_numbering_properties and next_item.has_numbering_properties:
                return True

        return False

    def export_borders(self, item, results, first_pass=True):
        if first_pass:
            for result in results:
                yield result
            return

        self.item = item

        prev_borders_properties = None
        prev_shading_properties = None

        border_properties = None
        shading_properties = None

        current_border_item = self.current_border_item.get(self.item_name)
        if current_border_item:
            item_properties = current_border_item.effective_properties
            prev_borders_properties = item_properties.border_properties
            prev_shading_properties = item_properties.shading_properties

        last_item = False
        close_border = True

        def prev_properties():
            return prev_borders_properties or prev_shading_properties

        def current_properties():
            return border_properties or shading_properties

        def properties_are_different():
            if border_properties != prev_borders_properties:
                return True
            elif shading_properties != prev_shading_properties:
                return True

            return False

        def pre_close():
            """Check if we should close the tag before yielding other tags"""
            self.item = item

            if not close_border:
                return
            elif prev_properties() is None:
                return

            # At this stage we need to make sure that if there is an previously open tag
            # about border/shading we need to close it
            yield self.close_tag()

        def post_close():
            """Check if we should close the tag once all the inner tags were yielded"""
            self.item = item

            if current_properties() and self.is_next_paragraph_listing():
                pass
            elif not last_item:
                return
            elif current_properties() is None:
                return

            # If the item with border/shading is the last one
            # we need to make sure that we close the tag
            yield self.close_tag()

        if item.effective_properties:
            border_properties = item.effective_properties.border_properties
            shading_properties = item.effective_properties.shading_properties

            if current_properties():
                last_item = self.is_last_item()
                close_border = False
                run_has_different_parent = False

                # If run is from different paragraph then we may need to draw separate border
                # even if border properties are the same
                if self.item_is_run and current_border_item:
                    if current_border_item.parent != item.parent:
                        run_has_different_parent = True

                if properties_are_different() or run_has_different_parent:
                    if prev_properties() is not None:
                        # We have a previous border/shading tag opened, so need to close it
                        yield HtmlTag(self.tag_name, closed=True)

                    # Open a new tag for the new border/shading and include all the properties
                    attrs = self.get_borders_property()
                    yield HtmlTag(self.tag_name, closed=False, **attrs)
                    self.current_border_item[self.item_name] = item

                if border_properties == prev_borders_properties:
                    border_between = getattr(border_properties, 'between', None)
                    add_between_border = bool(border_between)

                    if border_between and prev_borders_properties is not None:
                        if shading_properties:
                            if shading_properties == prev_shading_properties:
                                add_between_border = True
                            else:

                                add_between_border = prev_borders_properties.bottom != \
                                    border_between

                    if add_between_border:
                        # Render border between items
                        border_attrs = self.get_borders_property(only_between=True)
                        yield HtmlTag(self.tag_name, **border_attrs)
                        yield HtmlTag(self.tag_name, closed=True)

        for close_tag in pre_close():
            yield close_tag

        # All the inner items inside border/shading tag are issued here
        if results:
            for result in results:
                yield result

        for close_tag in post_close():
            yield close_tag

        self.prev_item = item

    def reset_top_border_if_the_same(self):
        if not self.prev_item or not self.prev_item.effective_properties:
            return False
        elif not self.prev_item.effective_properties.border_properties:
            return False
        elif not isinstance(self.prev_item, Paragraph):
            return False
        elif not isinstance(self.item, Paragraph):
            return False
        elif not self.item.have_same_numbering_properties_as(self.prev_item):
            return False

        curr_border_properties = self.item.effective_properties.border_properties
        prev_border_properties = self.prev_item.effective_properties.border_properties

        cur_top = curr_border_properties.top
        prev_bottom = prev_border_properties.bottom

        all_borders_defined = all([
            curr_border_properties.borders_have_same_properties(),
            prev_border_properties.borders_have_same_properties()
        ])

        if all_borders_defined and cur_top == prev_bottom:
            return True

        return False

    def get_borders_property(self, only_between=False):
        attrs = {}
        style = {}

        border_properties = self.item.effective_properties.border_properties
        shading_properties = self.item.effective_properties.shading_properties

        if border_properties:
            if only_between:
                style.update(border_properties.get_between_border_style())
            else:
                style.update(border_properties.get_padding_style())
                style.update(border_properties.get_shadow_style())
                border_style = border_properties.get_border_style()

                # We need to reset one border if adjacent identical borders are met
                if self.reset_top_border_if_the_same():
                    border_style['border-top'] = '0'
                style.update(border_style)

        if shading_properties and shading_properties.background_color:
            style['background-color'] = '#{0}'.format(shading_properties.background_color)

        if style:
            attrs['style'] = convert_dictionary_to_style_fragment(style)

        return attrs

    def export_close_paragraph_border(self):
        if self.current_border_item.get('Paragraph'):
            yield HtmlTag(self.TAGS['Paragraph'], closed=True)
            self.current_border_item['Paragraph'] = None

    def export_close_run_border(self):
        if self.current_border_item.get('Run'):
            yield HtmlTag(self.TAGS['Run'], closed=True)
            self.current_border_item['Run'] = None
