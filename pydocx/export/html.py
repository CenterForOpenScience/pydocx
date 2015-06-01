# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import posixpath
import xml.sax.saxutils
from itertools import chain, islice
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
from pydocx.export.base import PyDocXExporter, OldPyDocXExporter
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
            first.append(next(results))
            if not first:
                raise StopIteration

        for result in chain(first, results, [self.close()]):
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
        return ' '.join(
            '{k}="{v}"'.format(k=k, v=v)
            for k, v in
            sorted(self.attrs.items())
        )


class PyDocXHTMLExporter(PyDocXExporter):
    def __init__(self, *args, **kwargs):
        super(PyDocXHTMLExporter, self).__init__(*args, **kwargs)
        self.numbering_tracking = {}
        self.table_cell_rowspan_tracking = {}
        self.in_table_cell = False

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

            # Because this paragraph has a numbering def, it's active. This
            # controls whether or not a p tag will be generated
            numbering_tracking[paragraph]['active'] = True

            level = paragraph.get_numbering_level()
            if level is None:
                # TODO should trigger a break tag, but doesn't currently
                continue

            if num_def == previous_num_def:
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
                    numbering_tracking[paragraph]['close-item'] = True
                    numbering_tracking[paragraph]['open-item'] = True
                    # This level is less than the previous level
                    # Close the previous levels until we match up with this
                    # level
                    popped_levels = []
                    while levels:
                        if levels[-1] == level:
                            break
                        popped_level = levels.pop()
                        popped_levels.insert(0, popped_level)
                    # TODO what if previous_num_def_paragraph is None?
                    assert previous_num_def_paragraph
                    numbering_tracking[previous_num_def_paragraph]['close-level'] = popped_levels  # noqa
            elif previous_num_def is None:
                # There hasn't been a previous numbering definition
                numbering_tracking[paragraph]['open-level'] = level
                levels.append(level)
            else:
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
        return tag.apply(results)

    def _is_ordered_list(self, numbering_level):
        return numbering_level.num_format != 'bullet'

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
            raise StopIteration

        tracking = self.get_numbering_tracking(paragraph)
        if not tracking:
            raise StopIteration

        li = HtmlTag('li')
        if tracking.get('close-item'):
            yield li.close()

        if tracking.get('open-item'):
            yield li

        level = tracking.get('open-level')
        if level is not None:
            pydocx_class = 'pydocx-list-style-type-{fmt}'.format(
                fmt=level.num_format,
            )
            attrs = {}
            if self._is_ordered_list(level):
                attrs['class'] = pydocx_class
                yield HtmlTag('ol', **attrs)
            else:
                # unordered list implies bullet format, so don't pass the class
                yield HtmlTag('ul', **attrs)
            yield li
        raise StopIteration

    def export_numbering_level_end(self, paragraph):
        num_def = paragraph.get_numbering_definition()
        if not num_def:
            raise StopIteration

        tracking = self.get_numbering_tracking(paragraph)
        if not tracking:
            raise StopIteration

        levels = tracking.get('close-level', [])
        for level in reversed(levels):
            yield HtmlTag('li', closed=True)
            if self._is_ordered_list(level):
                yield HtmlTag('ol', closed=True)
            else:
                yield HtmlTag('ul', closed=True)
        raise StopIteration

    def get_paragraph_tag(self, paragraph):
        tracking = self.get_numbering_tracking(paragraph)
        if tracking and tracking.get('active'):
            return
        if self.in_table_cell:
            return
        return HtmlTag('p')

    def export_line_break_for_paragraph_if_needed(self, paragraph):
        # If multiple paragraphs are member of the same list item or same table
        # cell, instead of wrapping each paragraph with a paragraph tag,
        # separate the paragraphs with line breaks
        previous_from_parent = self.previous.get(paragraph.parent)
        if previous_from_parent is None:
            raise StopIteration

        if self.get_paragraph_tag(previous_from_parent) is not None:
            raise StopIteration

        tracking = self.get_numbering_tracking(paragraph)
        if tracking:
            if tracking.get('open-item') is not None:
                raise StopIteration

            if tracking.get('open-level') is not None:
                raise StopIteration

        previous_tracking = self.get_numbering_tracking(previous_from_parent)
        if previous_tracking:
            if previous_tracking.get('close-level') is not None:
                raise StopIteration

        line_break = wordprocessing.Break()
        for result in self.export_node(line_break):
            yield result

    def export_paragraph(self, paragraph):
        for result in self.export_numbering_level_begin(paragraph):
            yield result

        results = super(PyDocXHTMLExporter, self).export_paragraph(paragraph)
        tag = self.get_paragraph_tag(paragraph)
        if tag:
            results = tag.apply(results, allow_empty=False)
        else:
            line_break_results = self.export_line_break_for_paragraph_if_needed(paragraph)  # noqa
            results = chain(line_break_results, results)

        results = chain(results, self.export_numbering_level_end(paragraph))

        for result in results:
            yield result

    def export_paragraph_property_justification(self, paragraph, results):
        # TODO these classes should be applied on the paragraph, and not as
        # inline styles
        alignment = paragraph.effective_properties.justification
        if alignment in [JUSTIFY_LEFT, JUSTIFY_CENTER, JUSTIFY_RIGHT]:
            pydocx_class = 'pydocx-{alignment}'.format(
                alignment=alignment,
            )
            attrs = {
                'class': pydocx_class,
            }
            tag = HtmlTag('span', **attrs)
            results = tag.apply(results, allow_empty=False)
        return results

    def export_paragraph_property_indentation(self, paragraph, results):
        # TODO these classes should be applied on the paragraph, and not as
        # inline styles
        indentation = paragraph.effective_properties.indentation
        if indentation:
            right = indentation.get(INDENTATION_RIGHT)
            left = indentation.get(INDENTATION_LEFT)
            first_line = indentation.get(INDENTATION_FIRST_LINE)
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
                style['text-indent'] = '{0:.2f}em'.format(first_line)
            if style:
                attrs = {
                    'style': convert_dictionary_to_style_fragment(style)
                }
                tag = HtmlTag('span', **attrs)
            if tag:
                results = tag.apply(results, allow_empty=False)
        return results

    def export_run_property_bold(self, run, results):
        tag = HtmlTag('strong')
        return tag.apply(results)

    def export_run_property_italic(self, run, results):
        tag = HtmlTag('em')
        return tag.apply(results)

    def export_run_property_underline(self, run, results):
        attrs = {
            'class': 'pydocx-underline',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_run_property_caps(self, run, results):
        attrs = {
            'class': 'pydocx-caps',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_run_property_small_caps(self, run, results):
        attrs = {
            'class': 'pydocx-small-caps',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_run_property_dstrike(self, run, results):
        attrs = {
            'class': 'pydocx-strike',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_run_property_strike(self, run, results):
        attrs = {
            'class': 'pydocx-strike',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_run_property_vanish(self, run, results):
        attrs = {
            'class': 'pydocx-hidden',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

    def export_run_property_hidden(self, run, results):
        attrs = {
            'class': 'pydocx-hidden',
        }
        tag = HtmlTag('span', **attrs)
        return tag.apply(results)

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
        return tag.apply(results)

    def export_run_property_vertical_align_subscript(self, run, results):
        tag = HtmlTag('sub')
        return tag.apply(results)

    def export_text(self, text):
        results = super(PyDocXHTMLExporter, self).export_text(text)
        for result in results:
            if result:
                yield result

    def export_hyperlink(self, hyperlink):
        results = super(PyDocXHTMLExporter, self).export_hyperlink(hyperlink)
        target_uri = hyperlink.get_target_uri()
        if target_uri:
            href = self.escape(target_uri)
            tag = HtmlTag('a', href=href)
            results = tag.apply(results, allow_empty=False)

        # Prevent underline style from applying
        old = self.export_run_property_underline
        # TODO there's got to be a better way
        self.export_run_property_underline = lambda run, results: results
        for result in results:
            yield result
        self.export_run_property_underline = old

    def export_break(self, br):
        if br.is_page_break():
            tag_name = 'hr'
        else:
            tag_name = 'br'
        yield HtmlTag(tag_name, allow_self_closing=True)

    def calculate_table_cell_spans(self, table):
        if not table.rows:
            return

        active_rowspan_cells_by_column = {}
        cell_to_rowspan_count = defaultdict(int)
        for row in table.rows:
            for column_index, cell in enumerate(row.cells):
                properties = cell.properties
                # If this element is omitted, then this cell shall not be
                # part of any vertically merged grouping of cells, and any
                # vertically merged group of preceding cells shall be
                # closed.
                if properties is None or properties.vertical_merge is None:
                    # if properties are missing, this is the same as the
                    # the element being omitted
                    active_rowspan_cells_by_column[column_index] = None
                elif properties:
                    vertical_merge = properties.vertical_merge.get('val', 'continue')  # noqa
                    if vertical_merge == 'restart':
                        active_rowspan_cells_by_column[column_index] = cell
                        cell_to_rowspan_count[cell] += 1
                    elif vertical_merge == 'continue':
                        active_rowspan_for_column = active_rowspan_cells_by_column.get(column_index)  # noqa
                        if active_rowspan_for_column:
                            cell_to_rowspan_count[active_rowspan_for_column] += 1  # noqa
        return dict(cell_to_rowspan_count)

    def export_table(self, table):
        self.table_cell_rowspan_tracking[table] = self.calculate_table_cell_spans(table)  # noqa
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
            parent_table = list(islice(table_cell.nearest_ancestors(wordprocessing.Table), 0, 1))[0]  # noqa
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
            raise StopIteration
        image = None
        try:
            image = drawing.container.get_part_by_id(
                relationship_id=relationship_id,
            )
        except KeyError:
            pass
        return self.export_image(image=image, length=length, width=width)

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

    def export_image(self, image, length, width):
        image_src = self.get_image_source(image)
        if image_src:
            attrs = {
                'src': image_src,
            }
            if length and width:
                # The "width" in openxml is actually the height
                width_px = convert_emus_to_pixels(length)
                height_px = convert_emus_to_pixels(width)
                attrs['width'] = '{px:.0f}px'.format(px=width_px)
                attrs['height'] = '{px:.0f}px'.format(px=height_px)
            yield HtmlTag('img', allow_self_closing=True, **attrs)


class OldPyDocXHTMLExporter(OldPyDocXExporter):

    def __init__(self, *args, **kwargs):
        super(PyDocXHTMLExporter, self).__init__(*args, **kwargs)
        self.heading_level_conversion_map = {
            'heading 1': 'h1',
            'heading 2': 'h2',
            'heading 3': 'h3',
            'heading 4': 'h4',
            'heading 5': 'h5',
            'heading 6': 'h6',
        }
        self.default_heading_level = 'h6'

    def load_document(self):
        document = super(PyDocXHTMLExporter, self).load_document()

        # Disable character styling for headers
        if self.style_definitions_part:
            for style in self.style_definitions_part.styles.styles:
                style_name = style.name.lower()
                if self.style_name_is_a_heading_level(style_name):
                    style.run_properties = None

        return document

    @property
    def parsed(self):
        content = super(PyDocXHTMLExporter, self).parsed
        content = '<html>{header}<body>{body}{footer}</body></html>'.format(
            header=self.head(),
            body=content,
            footer=self.footer(),
        )
        return content

    @property
    def parsed_content(self):
        return super(PyDocXHTMLExporter, self).parsed

    def make_element(self, tag, contents='', attrs=None):
        if attrs:
            attrs = convert_dictionary_to_html_attributes(attrs)
            template = '<{tag} {attrs}>{contents}</{tag}>'
        else:
            template = '<{tag}>{contents}</{tag}>'
        return template.format(
            tag=tag,
            attrs=attrs,
            contents=contents,
        )

    def head(self):
        head = [
            '<meta charset="utf-8" />',
            self.style(),
        ]
        return self.make_element(
            tag='head',
            contents=''.join(head),
        )

    def footer(self):
        return self.footnotes()

    def footnotes(self):
        footnotes = [
            self.footnote(self.footnote_id_to_content[footnote_id])
            for footnote_id in self.footnote_ordering
        ]
        if footnotes:
            return '{page_break}{footnotes}'.format(
                page_break=self.page_break(),
                footnotes=self.ordered_list(
                    text=''.join(footnotes),
                    list_style='decimal',
                )
            )
        else:
            return ''

    def footnote_ref(self, footnote_id):
        return self.make_element(
            tag='a',
            attrs=dict(
                href='#footnote-ref-{id}',
                name='footnote-{id}'
            ),
            contents='^',
        ).format(id=footnote_id)

    def footnote(self, content):
        return self.make_element(
            tag='li',
            contents=content,
        )

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

        return self.make_element(
            tag='style',
            contents=''.join(result),
        )

    def footnote_reference(self, footnote_id, index):
        anchor = self.make_element(
            tag='a',
            attrs=dict(
                href='#footnote-{id}',
                name='footnote-ref-{id}'
            ),
            contents='{index}',
        )
        return anchor.format(
            id=footnote_id,
            index=index,
        )

    def escape(self, text):
        return xml.sax.saxutils.quoteattr(text)[1:-1]

    def linebreak(self, pre=None):
        return '<br />'

    def paragraph(self, text, pre=None):
        return self.make_element(
            tag='p',
            contents=text,
        )

    def heading(self, text, heading_style_name):
        heading_value = self.heading_level_conversion_map.get(
            heading_style_name,
            self.default_heading_level,
        )
        return self.make_element(
            tag=heading_value,
            contents=text,
        )

    def insertion(self, text, author, date):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-insert',
            },
        )

    def hyperlink(self, text, href):
        if text == '':
            return ''
        return self.make_element(
            tag='a',
            contents=text,
            attrs={
                'href': href,
            },
        )

    def image_handler(self, image_data, filename, uri_is_external):
        if uri_is_external:
            return image_data
        extension = filename.split('.')[-1].lower()
        b64_encoded_src = 'data:image/%s;base64,%s' % (
            extension,
            base64.b64encode(image_data).decode(),
        )
        b64_encoded_src = self.escape(b64_encoded_src)
        return b64_encoded_src

    def image(self, image_data, filename, x, y, uri_is_external):
        src = self.image_handler(image_data, filename, uri_is_external)
        if not src:
            return ''
        if all([x, y]):
            return '<img src="%s" height="%s" width="%s" />' % (
                src,
                y,
                x,
            )
        else:
            return '<img src="%s" />' % src

    def deletion(self, text, author, date):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-delete',
            },
        )

    def list_element(self, text):
        return self.make_element(
            tag='li',
            contents=text,
        )

    def ordered_list(self, text, list_style):
        class_name = 'pydocx-list-style-type-{list_style}'.format(
            list_style=list_style,
        )
        return self.make_element(
            tag='ol',
            contents=text,
            attrs={
                'class': class_name,
            }
        )

    def unordered_list(self, text):
        return self.make_element(
            tag='ul',
            contents=text,
        )

    def bold(self, text):
        return self.make_element(
            tag='strong',
            contents=text,
        )

    def italics(self, text):
        return self.make_element(
            tag='em',
            contents=text,
        )

    def underline(self, text):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-underline',
            },
        )

    def caps(self, text):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-caps',
            },
        )

    def small_caps(self, text):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-small-caps',
            },
        )

    def strike(self, text):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-strike',
            },
        )

    def hide(self, text):
        return self.make_element(
            tag='span',
            contents=text,
            attrs={
                'class': 'pydocx-hidden',
            },
        )

    def superscript(self, text):
        return self.make_element(
            tag='sup',
            contents=text,
        )

    def subscript(self, text):
        return self.make_element(
            tag='sub',
            contents=text,
        )

    def tab(self):
        return self.make_element(
            tag='span',
            contents=' ',
            attrs={
                'class': 'pydocx-tab',
            },
        )

    def table(self, text):
        return self.make_element(
            tag='table',
            contents=text,
            attrs={
                'border': '1',
            },
        )

    def table_row(self, text):
        return self.make_element(
            tag='tr',
            contents=text,
        )

    def table_cell(self, text, col='', row=''):
        attrs = {}
        if col:
            attrs['colspan'] = col
        if row:
            attrs['rowspan'] = row
        return self.make_element(
            tag='td',
            contents=text,
            attrs=attrs,
        )

    def page_break(self):
        return '<hr />'

    def indent(
        self,
        text,
        alignment=None,
        firstLine=None,
        left=None,
        right=None,
    ):
        attrs = {}
        if alignment:
            attrs['class'] = 'pydocx-%s' % alignment
        style = {}
        if firstLine:
            firstLine = convert_twips_to_ems(firstLine)
            style['text-indent'] = '%.2fem' % firstLine
        if left:
            left = convert_twips_to_ems(left)
            style['margin-left'] = '%.2fem' % left
        if right:
            right = convert_twips_to_ems(right)
            style['margin-right'] = '%.2fem' % right
        if style:
            attrs['style'] = convert_dictionary_to_style_fragment(style)
        return self.make_element(
            tag='span',
            contents=text,
            attrs=attrs,
        )

    def break_tag(self):
        return '<br />'
