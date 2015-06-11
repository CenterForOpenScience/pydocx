# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import posixpath
from itertools import chain
from collections import defaultdict

from pydocx.constants import (
    INDENTATION_FIRST_LINE,
    INDENTATION_LEFT,
    INDENTATION_RIGHT,
    JUSTIFY_CENTER,
    JUSTIFY_LEFT,
    JUSTIFY_RIGHT,
    POINTS_PER_EM,
    PYDOCX_STYLES,
    TWIPS_PER_POINT,
    EMUS_PER_PIXEL,
)
from pydocx.export.base import PyDocXExporter
from pydocx.openxml import wordprocessing
from pydocx.util.uri import uri_is_external
from pydocx.util.xml import (
    convert_dictionary_to_html_attributes,
    convert_dictionary_to_style_fragment,
)


def convert_twips_to_ems(value):
    '''
    >>> convert_twips_to_ems(30)
    0.125
    '''
    return value / TWIPS_PER_POINT / POINTS_PER_EM


def convert_emus_to_pixels(emus):
    return emus / EMUS_PER_PIXEL


def get_first_from_sequence(sequence, default=None):
    first_result = default
    try:
        first_result = next(sequence)
    except StopIteration:
        pass
    return first_result


class HtmlTag(object):
    closed_tag_format = '</{tag}>'

    def __init__(self, tag, allow_self_closing=False, closed=False, **attrs):
        self.tag = tag
        self.allow_self_closing = allow_self_closing
        self.attrs = attrs
        self.closed = closed

    def apply(self, results, allow_empty=True):
        first = [self]
        if not allow_empty:
            first_result = get_first_from_sequence(results)
            if not first_result:
                return
            first.append(first_result)

        sequence = [first, results]

        if not self.allow_self_closing:
            sequence.append([self.close()])

        results = chain(*sequence)

        for result in results:
            yield result

    def close(self):
        return HtmlTag(
            tag=self.tag,
            closed=True,
        )

    def to_html(self):
        if self.closed is True:
            return self.closed_tag_format.format(tag=self.tag)
        else:
            attrs = self.get_html_attrs()
            end_bracket = '>'
            if self.allow_self_closing:
                end_bracket = ' />'
            if attrs:
                return '<{tag} {attrs}{end}'.format(
                    tag=self.tag,
                    attrs=attrs,
                    end=end_bracket,
                )
            else:
                return '<{tag}{end}'.format(tag=self.tag, end=end_bracket)

    def get_html_attrs(self):
        return convert_dictionary_to_html_attributes(self.attrs)


class PyDocXHTMLExporter(PyDocXExporter):
    def __init__(self, *args, **kwargs):
        super(PyDocXHTMLExporter, self).__init__(*args, **kwargs)
        self.numbering_tracking = {}
        self.table_cell_rowspan_tracking = {}
        self.in_table_cell = False
        self.heading_level_conversion_map = {
            'heading 1': 'h1',
            'heading 2': 'h2',
            'heading 3': 'h3',
            'heading 4': 'h4',
            'heading 5': 'h5',
            'heading 6': 'h6',
        }
        self.default_heading_level = 'h6'

    def head(self):
        tag = HtmlTag('head')
        results = chain(self.meta(), self.style())
        return tag.apply(results)

    def style(self):
        styles = {
            'body': {
                'margin': '0px auto',
            }
        }

        if self.page_width:
            width = self.page_width / POINTS_PER_EM
            styles['body']['width'] = '%.2fem' % width

        result = []
        for name, definition in sorted(PYDOCX_STYLES.items()):
            result.append('.pydocx-%s {%s}' % (
                name,
                convert_dictionary_to_style_fragment(definition),
            ))

        for name, definition in sorted(styles.items()):
            result.append('%s {%s}' % (
                name,
                convert_dictionary_to_style_fragment(definition),
            ))

        tag = HtmlTag('style')
        return tag.apply(''.join(result))

    def meta(self):
        yield HtmlTag('meta', charset='utf-8', allow_self_closing=True)

    def export(self):
        return ''.join(
            result.to_html() if isinstance(result, HtmlTag)
            else result
            for result in super(PyDocXHTMLExporter, self).export()
        )

    def export_document(self, document):
        tag = HtmlTag('html')
        results = super(PyDocXHTMLExporter, self).export_document(document)
        return tag.apply(chain(self.head(), results))

    def calculate_numbering_spans(self, paragraphs):
        numbering_tracking = defaultdict(dict)

        previous_num_def = None
        previous_num_def_paragraph = None
        previous_num_def_paragraph_index = 0
        levels = []

        possible_numbering_paragraphs = []

        # * If this is the final list item for the def, close the def
        # * If this is the first list item for the def, open the def
        # * If the def = prev and level = prev,
        # then close the list item and open a new one
        # * If the def = prev, and level + prev,
        # then open a new list, open a new list item
        # * If the def = prev, and level - prev,
        # then close the previous level
        for index, paragraph in enumerate(paragraphs):
            num_def = paragraph.get_numbering_definition()

            if previous_num_def is not None:
                # There is a previous numbering def, so it could be part of
                # that previous list. We won't know until we process all of the
                # paragraphs.
                possible_numbering_paragraphs.append((index, paragraph))

            if num_def is None:
                continue

            level = paragraph.get_numbering_level()
            if level is None:
                continue

            # Because this paragraph has a numbering def, it's active. This
            # controls whether or not a p tag will be generated
            numbering_tracking[paragraph]['active'] = True

            open_new_level = False
            open_new_list = False
            continue_current_list = False

            if previous_num_def is None:
                open_new_level = True
            elif num_def == previous_num_def:
                continue_current_list = True
            elif previous_num_def is not None and num_def != previous_num_def:
                open_new_list = True

            if paragraph.get_heading_style():
                # A paragraph that is defined a a heading never opens a new
                # list. So if a heading has level 0 numbering, that numbering
                # is ignored. However, if a heading appears as a sub-level,
                # instead of opening that new level, it is appended to the
                # content of the current item, one level up
                # If we have a paragraph defined as a heading style at the root
                # level of a numbering list

                previous_num_def_paragraph = paragraph
                previous_num_def_paragraph_index = index

                # Don't set previous_num_def here because we are ignoring this
                # paragraph's level information

                # prevent levels from being opened / closed for this paragraph
                continue

            if open_new_level:
                # There hasn't been a previous numbering definition
                numbering_tracking[paragraph]['open-level'] = level
                levels.append(level)

            if continue_current_list:
                assert levels
                level_id = int(level.level_id)
                previous_level = levels[-1]
                previous_level_id = int(previous_level.level_id)
                if level_id == previous_level_id:
                    # The level hasn't changed
                    numbering_tracking[paragraph]['close-item'] = True
                    numbering_tracking[paragraph]['open-item'] = True
                elif level_id > previous_level_id:
                    # This level is greater than the previous level, so
                    # start a new level
                    numbering_tracking[paragraph]['open-level'] = level
                    levels.append(level)
                elif level_id < previous_level_id:
                    # This level is less than the previous level
                    # Close the previous levels until we match up with this
                    # level
                    popped_levels = []
                    while levels:
                        # Pop levels until we get to level, or lower
                        previous_level = levels[-1]
                        previous_level_id = int(previous_level.level_id)
                        if previous_level_id <= level_id:
                            break
                        popped_level = levels.pop()
                        popped_levels.insert(0, popped_level)
                    if levels:
                        numbering_tracking[paragraph]['close-item'] = True
                        numbering_tracking[paragraph]['open-item'] = True
                    else:
                        # This handles the mangled level case
                        levels = [level]
                        numbering_tracking[paragraph]['open-level'] = level

                    # TODO could previous_num_def_paragraph ever be None?
                    assert previous_num_def_paragraph
                    numbering_tracking[previous_num_def_paragraph]['close-level'] = popped_levels  # noqa

            if open_new_list:
                # The num def has changed
                # Close all of the levels and open the new definition
                assert previous_num_def_paragraph
                numbering_tracking[previous_num_def_paragraph]['close-level'] = levels  # noqa
                numbering_tracking[paragraph]['open-level'] = level
                levels = [level]

                # Bare paragraphs contained within the numbering span are
                # considered a part of the numbering span
                for index, paragraph in possible_numbering_paragraphs:
                    if index < previous_num_def_paragraph_index:
                        numbering_tracking[paragraph]['active'] = True

                possible_numbering_paragraphs = []

            previous_num_def = num_def
            previous_num_def_paragraph = paragraph
            previous_num_def_paragraph_index = index

        if previous_num_def is not None:
            # Finalize the previous numbering definition if it exists
            assert previous_num_def_paragraph
            numbering_tracking[previous_num_def_paragraph]['close-level'] = levels  # noqa

        # Bare paragraphs contained within the numbering span are considered a
        # part of the numbering span
        for index, paragraph in possible_numbering_paragraphs:
            if index < previous_num_def_paragraph_index:
                numbering_tracking[paragraph]['active'] = True

        return numbering_tracking

    def export_body(self, body):
        self.numbering_tracking[body] = self.calculate_numbering_spans(
            item
            for item in body.children
            if isinstance(item, wordprocessing.Paragraph)
        )

        results = super(PyDocXHTMLExporter, self).export_body(body)
        tag = HtmlTag('body')
        return tag.apply(chain(results, self.footer()))

    def footer(self):
        for result in self.export_footnotes():
            yield result

    def export_footnotes(self):
        results = super(PyDocXHTMLExporter, self).export_footnotes()
        attrs = {
            'class': 'pydocx-list-style-type-decimal',
        }
        ol = HtmlTag('ol', **attrs)
        results = ol.apply(results, allow_empty=False)

        page_break = HtmlTag('hr', allow_self_closing=True)
        return page_break.apply(results, allow_empty=False)

    def export_footnote(self, footnote):
        results = super(PyDocXHTMLExporter, self).export_footnote(footnote)
        tag = HtmlTag('li')
        return tag.apply(results, allow_empty=False)

    def _is_ordered_list(self, numbering_level):
        return not numbering_level.is_bullet_format()

    def get_numbering_tracking(self, paragraph):
        numbering_tracking = self.numbering_tracking.get(paragraph.parent)
        if not numbering_tracking:
            return

        tracking = numbering_tracking.get(paragraph)
        if not tracking:
            return

        return tracking

    def export_numbering_level_begin(self, paragraph):
        num_def = paragraph.get_numbering_definition()
        if not num_def:
            return

        tracking = self.get_numbering_tracking(paragraph)
        if not tracking:
            return

        li = HtmlTag('li')
        if tracking.get('close-item'):
            yield li.close()

        if tracking.get('open-item'):
            yield li

        level = tracking.get('open-level')
        if level is not None:
            tag = self.get_numbering_level_tag_begin(paragraph)
            yield tag
            yield li

    def export_numbering_level_end(self, paragraph):
        tracking = self.get_numbering_tracking(paragraph)
        if not tracking:
            return

        levels = tracking.get('close-level', [])
        for level in reversed(levels):
            yield HtmlTag('li', closed=True)
            if self._is_ordered_list(level):
                yield HtmlTag('ol', closed=True)
            else:
                yield HtmlTag('ul', closed=True)

    def get_paragraph_tag(self, paragraph):
        heading_style = paragraph.get_heading_style()
        if heading_style:
            return self.get_heading_tag(heading_style)
        if self.in_table_cell:
            return
        tracking = self.get_numbering_tracking(paragraph)
        if tracking and tracking.get('active'):
            return
        if paragraph.has_structured_document_parent():
            return
        return HtmlTag('p')

    def get_heading_tag(self, heading_style):
        tag = self.heading_level_conversion_map.get(
            heading_style.name.lower(),
            self.default_heading_level,
        )
        return HtmlTag(tag)

    def should_yield_line_break_for_paragraph(self, paragraph):
        # If multiple paragraphs are member of the same list item or same table
        # cell, instead of wrapping each paragraph with a paragraph tag,
        # separate the paragraphs with line breaks
        previous_from_parent = self.previous.get(paragraph.parent)
        if previous_from_parent is None:
            return False

        if not isinstance(previous_from_parent, wordprocessing.Paragraph):
            return False

        if self.get_paragraph_tag(previous_from_parent) is not None:
            return False

        tracking = self.get_numbering_tracking(paragraph)
        if tracking:
            if tracking.get('open-item') is not None:
                return False

            if tracking.get('open-level') is not None:
                return False

        previous_tracking = self.get_numbering_tracking(previous_from_parent)
        if previous_tracking:
            if previous_tracking.get('close-level') is not None:
                return False

        # TODO Do not output a break tag if the previous paragraph was empty
        return True

    def export_line_break_for_paragraph_if_needed(self, paragraph):
        if self.should_yield_line_break_for_paragraph(paragraph):
            line_break = wordprocessing.Break()
            for result in self.export_node(line_break):
                yield result

    def export_paragraph(self, paragraph):
        for result in self.export_numbering_level_begin(paragraph):
            yield result

        results = super(PyDocXHTMLExporter, self).export_paragraph(paragraph)

        # TODO I could see this section being its own helper method. that would
        # make it possible to just return a chain() for everything here
        tag = self.get_paragraph_tag(paragraph)
        if tag:
            results = tag.apply(results, allow_empty=False)
        else:
            line_break_results = self.export_line_break_for_paragraph_if_needed(paragraph)  # noqa
            first_result = get_first_from_sequence(results)
            if first_result:
                results = chain(
                    line_break_results,
                    [first_result],
                    results,
                )
        results = chain(results, self.export_numbering_level_end(paragraph))

        for result in results:
            yield result

    def export_paragraph_property_justification(self, paragraph, results):
        # TODO these classes could be applied on the paragraph, and not as
        # inline spans
        alignment = paragraph.effective_properties.justification
        # TODO These alignment values are for traditional conformance. Strict
        # conformance uses different values
        if alignment in [JUSTIFY_LEFT, JUSTIFY_CENTER, JUSTIFY_RIGHT]:
            pydocx_class = 'pydocx-{alignment}'.format(
                alignment=alignment,
            )
            attrs = {
                'class': pydocx_class,
            }
            tag = HtmlTag('span', **attrs)
            results = tag.apply(results, allow_empty=False)
        elif alignment is not None:
            # TODO What if alignment is something else?
            pass
        return results

    def export_paragraph_property_indentation(self, paragraph, results):
        # TODO these classes should be applied on the paragraph, and not as
        # inline styles
        indentation = paragraph.effective_properties.indentation
        if indentation:
            # TODO add test cases that use other indentation types
            right = indentation.get(INDENTATION_RIGHT)
            left = indentation.get(INDENTATION_LEFT)
            first_line = indentation.get(INDENTATION_FIRST_LINE)
            # TODO would be nice if this integer conversion was handled
            # implicitly by the model somehow
            if right:
                try:
                    right = int(right)
                except ValueError:
                    right = None
            if left:
                try:
                    left = int(left)
                except ValueError:
                    left = None
            if first_line:
                try:
                    first_line = int(first_line)
                except ValueError:
                    first_line = None
            style = {}
            if right:
                right = convert_twips_to_ems(right)
                style['margin-right'] = '{0:.2f}em'.format(right)
            if left:
                left = convert_twips_to_ems(left)
                style['margin-left'] = '{0:.2f}em'.format(left)
            if first_line:
                first_line = convert_twips_to_ems(first_line)
                # TODO text-indent doesn't work with inline elements like span
                style['text-indent'] = '{0:.2f}em'.format(first_line)
            if style:
                attrs = {
                    'style': convert_dictionary_to_style_fragment(style)
                }
                tag = HtmlTag('span', **attrs)
                results = tag.apply(results, allow_empty=False)
        return results

    def get_run_styles_to_apply(self, run):
        parent_paragraphs = run.nearest_ancestors(wordprocessing.Paragraph)
        parent_paragraph = get_first_from_sequence(parent_paragraphs)
        if parent_paragraph and parent_paragraph.get_heading_style():
            # If the parent paragraph is a heading, return an empty generator
            return
        results = super(PyDocXHTMLExporter, self).get_run_styles_to_apply(run)
        for result in results:
            yield result

    def export_run_property_bold(self, run, results):
        tag = HtmlTag('strong')
        return tag.apply(results, allow_empty=False)

    def export_run_property_italic(self, run, results):
        tag = HtmlTag('em')
        return tag.apply(results, allow_empty=False)

    def export_run_property_underline(self, run, results):
        attrs = {
            'class': 'pydocx-underline',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_caps(self, run, results):
        attrs = {
            'class': 'pydocx-caps',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_small_caps(self, run, results):
        attrs = {
            'class': 'pydocx-small-caps',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_dstrike(self, run, results):
        attrs = {
            'class': 'pydocx-strike',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_strike(self, run, results):
        attrs = {
            'class': 'pydocx-strike',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_vanish(self, run, results):
        attrs = {
            'class': 'pydocx-hidden',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_hidden(self, run, results):
        attrs = {
            'class': 'pydocx-hidden',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def export_run_property_vertical_align(self, run, results):
        if run.effective_properties.is_superscript():
            return self.export_run_property_vertical_align_superscript(
                run,
                results,
            )
        elif run.effective_properties.is_subscript():
            return self.export_run_property_vertical_align_subscript(
                run,
                results,
            )
        return results

    def export_run_property_vertical_align_superscript(self, run, results):
        tag = HtmlTag('sup')
        return tag.apply(results, allow_empty=False)

    def export_run_property_vertical_align_subscript(self, run, results):
        tag = HtmlTag('sub')
        return tag.apply(results, allow_empty=False)

    def export_text(self, text):
        results = super(PyDocXHTMLExporter, self).export_text(text)
        for result in results:
            if result:
                yield result

    def export_deleted_text(self, deleted_text):
        # TODO deleted_text should be ignored if it is NOT contained within a
        # deleted run
        results = self.export_text(deleted_text)
        attrs = {
            'class': 'pydocx-delete',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results, allow_empty=False)

    def get_hyperlink_tag(self, hyperlink):
        target_uri = hyperlink.get_target_uri()
        if target_uri:
            href = self.escape(target_uri)
            return HtmlTag('a', href=href)

    def export_hyperlink(self, hyperlink):
        results = super(PyDocXHTMLExporter, self).export_hyperlink(hyperlink)
        tag = self.get_hyperlink_tag(hyperlink)
        if tag:
            results = tag.apply(results, allow_empty=False)

        # Prevent underline style from applying by temporarily monkey-patching
        # the export unliner function. There's got to be a better way.
        old = self.export_run_property_underline
        self.export_run_property_underline = lambda run, results: results
        for result in results:
            yield result
        self.export_run_property_underline = old

    def get_break_tag(self, br):
        if br.is_page_break():
            tag_name = 'hr'
        else:
            tag_name = 'br'
        return HtmlTag(tag_name, allow_self_closing=True)

    def export_break(self, br):
        tag = self.get_break_tag(br)
        yield tag

    def export_table(self, table):
        table_cell_spans = table.calculate_table_cell_spans()
        self.table_cell_rowspan_tracking[table] = table_cell_spans
        results = super(PyDocXHTMLExporter, self).export_table(table)
        tag = HtmlTag('table', border='1')
        return tag.apply(results)

    def export_table_row(self, table_row):
        results = super(PyDocXHTMLExporter, self).export_table_row(table_row)
        tag = HtmlTag('tr')
        return tag.apply(results)

    def export_table_cell(self, table_cell):
        self.numbering_tracking[table_cell] = self.calculate_numbering_spans(
            item
            for item in table_cell.children
            if isinstance(item, wordprocessing.Paragraph)
        )

        start_new_tag = False
        colspan = 1
        if table_cell.properties:
            if table_cell.properties.should_close_previous_vertical_merge():
                start_new_tag = True
            try:
                # Should be done by properties, or as a helper
                colspan = int(table_cell.properties.grid_span)
            except (TypeError, ValueError):
                colspan = 1

        else:
            # This means the properties element is missing, which means the
            # merge element is missing
            start_new_tag = True

        tag = None
        if start_new_tag:
            parent_tables = table_cell.nearest_ancestors(wordprocessing.Table)
            parent_table = get_first_from_sequence(parent_tables)
            rowspan_counts = self.table_cell_rowspan_tracking[parent_table]
            rowspan = rowspan_counts.get(table_cell, 1)
            attrs = {}
            if colspan > 1:
                attrs['colspan'] = colspan
            if rowspan > 1:
                attrs['rowspan'] = rowspan
            tag = HtmlTag('td', **attrs)

        results = super(PyDocXHTMLExporter, self).export_table_cell(table_cell)
        if tag:
            results = tag.apply(results)

        self.in_table_cell = True
        for result in results:
            yield result
        self.in_table_cell = False

    def export_drawing(self, drawing):
        length, width = drawing.get_picture_extents()
        relationship_id = drawing.get_picture_relationship_id()
        if not relationship_id:
            return
        image = None
        try:
            image = drawing.container.get_part_by_id(
                relationship_id=relationship_id,
            )
        except KeyError:
            pass
        attrs = {}
        if length and width:
            # The "width" in openxml is actually the height
            width_px = '{px:.0f}px'.format(px=convert_emus_to_pixels(length))
            height_px = '{px:.0f}px'.format(px=convert_emus_to_pixels(width))
            attrs['width'] = width_px
            attrs['height'] = height_px
        return self.export_image(image=image, **attrs)

    def get_image_source(self, image):
        if image is None:
            return
        elif uri_is_external(image.uri):
            return image.uri
        else:
            data = image.stream.read()
            _, filename = posixpath.split(image.uri)
            extension = filename.split('.')[-1].lower()
            b64_encoded_src = 'data:image/{ext};base64,{data}'.format(
                ext=extension,
                data=base64.b64encode(data).decode(),
            )
            return self.escape(b64_encoded_src)

    def export_image(self, image, width=None, height=None):
        image_src = self.get_image_source(image)
        if image_src:
            attrs = {
                'src': image_src,
            }
            if width and height:
                attrs['width'] = width
                attrs['height'] = height
            yield HtmlTag('img', allow_self_closing=True, **attrs)

    def export_inserted_run(self, inserted_run):
        results = super(PyDocXHTMLExporter, self).export_inserted_run(inserted_run)  # noqa
        attrs = {
            'class': 'pydocx-insert',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_vml_image_data(self, image_data):
        width, height = image_data.get_picture_extents()
        if not image_data.relationship_id:
            return
        image = None
        try:
            image = image_data.container.get_part_by_id(
                relationship_id=image_data.relationship_id,
            )
        except KeyError:
            pass
        return self.export_image(image=image, width=width, height=height)

    def export_footnote_reference(self, footnote_reference):
        results = super(PyDocXHTMLExporter, self).export_footnote_reference(
            footnote_reference,
        )
        footnote_id = footnote_reference.footnote_id
        href = '#footnote-{fid}'.format(fid=footnote_id)
        name = 'footnote-ref-{fid}'.format(fid=footnote_id)
        tag = HtmlTag('a', href=href, name=name)
        for result in tag.apply(results, allow_empty=False):
            yield result

    def export_footnote_reference_mark(self, footnote_reference_mark):
        footnote_parents = footnote_reference_mark.nearest_ancestors(
            wordprocessing.Footnote,
        )
        footnote_parent = get_first_from_sequence(footnote_parents)
        if not footnote_parent:
            return

        footnote_id = footnote_parent.footnote_id
        if not footnote_id:
            return

        name = 'footnote-{fid}'.format(fid=footnote_id)
        href = '#footnote-ref-{fid}'.format(fid=footnote_id)
        tag = HtmlTag('a', href=href, name=name)
        results = tag.apply(['^'])
        for result in results:
            yield result

    def export_tab_char(self, tab_char):
        results = super(PyDocXHTMLExporter, self).export_tab_char(tab_char)
        attrs = {
            'class': 'pydocx-tab',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)
