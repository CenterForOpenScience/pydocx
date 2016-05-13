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

from pydocx.constants import (
    JUSTIFY_CENTER,
    JUSTIFY_LEFT,
    JUSTIFY_RIGHT,
    POINTS_PER_EM,
    PYDOCX_STYLES,
    TWIPS_PER_POINT,
    EMUS_PER_PIXEL,
)
from pydocx.export.base import PyDocXExporter
from pydocx.export.numbering_span import NumberingItem
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
    '''
    Given a sequence, return the first item in the sequence. If the sequence is
    empty, return the passed in default.
    '''
    first_result = default
    try:
        first_result = next(sequence)
    except StopIteration:
        pass
    return first_result


def is_only_whitespace(obj):
    '''
    If the obj has `strip` return True if calling strip on the obj results in
    an empty instance. Otherwise, return False.
    '''
    if hasattr(obj, 'strip'):
        return not obj.strip()
    return False


def is_not_empty_and_not_only_whitespace(gen):
    '''
    Determine if a generator is empty, or consists only of whitespace.

    If the generator is non-empty, return the original generator. Otherwise,
    return None
    '''
    queue = []
    if gen is None:
        return
    try:
        for item in gen:
            queue.append(item)
            is_whitespace = True
            if isinstance(item, HtmlTag):
                # If we encounter a tag that allows whitespace, then we can stop
                is_whitespace = not item.allow_whitespace
            else:
                is_whitespace = is_only_whitespace(item)

            if not is_whitespace:
                # This item isn't whitespace, so we're done scanning
                return chain(queue, gen)

    except StopIteration:
        pass


class HtmlTag(object):
    closed_tag_format = '</{tag}>'

    def __init__(
        self,
        tag,
        allow_self_closing=False,
        closed=False,
        allow_whitespace=False,
        **attrs
    ):
        self.tag = tag
        self.allow_self_closing = allow_self_closing
        self.attrs = attrs
        self.closed = closed
        self.allow_whitespace = allow_whitespace

    def apply(self, results, allow_empty=True):
        if not allow_empty:
            results = is_not_empty_and_not_only_whitespace(results)
            if results is None:
                return

        sequence = [[self]]
        if results is not None:
            sequence.append(results)

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
        sequence = []
        head = self.head()
        if head is not None:
            sequence.append(head)
        if results is not None:
            sequence.append(results)
        return tag.apply(chain(*sequence))

    def export_body(self, body):
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

    def get_paragraph_tag(self, paragraph):
        heading_style = paragraph.heading_style
        if heading_style:
            tag = self.get_heading_tag(paragraph)
            if tag:
                return tag
        if self.in_table_cell:
            return
        if paragraph.has_structured_document_parent():
            return
        if isinstance(paragraph.parent, NumberingItem):
            return
        return HtmlTag('p')

    def get_heading_tag(self, paragraph):
        if paragraph.has_ancestor(NumberingItem):
            # Force-bold headings that appear in list items
            return HtmlTag('strong')
        heading_style = paragraph.heading_style
        tag = self.heading_level_conversion_map.get(
            heading_style.name.lower(),
            self.default_heading_level,
        )
        return HtmlTag(tag)

    def export_paragraph(self, paragraph):
        results = super(PyDocXHTMLExporter, self).export_paragraph(paragraph)

        results = is_not_empty_and_not_only_whitespace(results)
        if results is None:
            return

        tag = self.get_paragraph_tag(paragraph)
        if tag:
            results = tag.apply(results)

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
        properties = paragraph.effective_properties

        style = {}

        if properties.indentation_right:
            # TODO would be nice if this integer conversion was handled
            # implicitly by the model somehow
            try:
                right = int(properties.indentation_right)
            except ValueError:
                right = None

            if right:
                right = convert_twips_to_ems(right)
                style['margin-right'] = '{0:.2f}em'.format(right)

        if properties.indentation_left:
            # TODO would be nice if this integer conversion was handled
            # implicitly by the model somehow
            try:
                left = int(properties.indentation_left)
            except ValueError:
                left = None

            if left:
                left = convert_twips_to_ems(left)
                style['margin-left'] = '{0:.2f}em'.format(left)

        if properties.indentation_first_line:
            # TODO would be nice if this integer conversion was handled
            # implicitly by the model somehow
            try:
                first_line = int(properties.indentation_first_line)
            except ValueError:
                first_line = None

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
        parent_paragraph = run.get_first_ancestor(wordprocessing.Paragraph)
        if parent_paragraph and parent_paragraph.heading_style:
            results = self.get_run_styles_to_apply_for_heading(run)
        else:
            results = super(PyDocXHTMLExporter, self).get_run_styles_to_apply(run)
        for result in results:
            yield result

    def get_run_styles_to_apply_for_heading(self, run):
        allowed_handlers = set([
            self.export_run_property_italic,
            self.export_run_property_hidden,
            self.export_run_property_vanish,
        ])

        handlers = super(PyDocXHTMLExporter, self).get_run_styles_to_apply(run)
        for handler in handlers:
            if handler in allowed_handlers:
                yield handler

    def export_run_property(self, tag, run, results):
        # Any leading whitespace in the run is not styled.
        for result in results:
            if is_only_whitespace(result):
                yield result
            else:
                # We've encountered something that isn't explicit whitespace
                results = chain([result], results)
                break
        else:
            results = None

        if results:
            for result in tag.apply(results):
                yield result

    def export_run_property_bold(self, run, results):
        tag = HtmlTag('strong')
        return self.export_run_property(tag, run, results)

    def export_run_property_italic(self, run, results):
        tag = HtmlTag('em')
        return self.export_run_property(tag, run, results)

    def export_run_property_underline(self, run, results):
        attrs = {
            'class': 'pydocx-underline',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

    def export_run_property_caps(self, run, results):
        attrs = {
            'class': 'pydocx-caps',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

    def export_run_property_small_caps(self, run, results):
        attrs = {
            'class': 'pydocx-small-caps',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

    def export_run_property_dstrike(self, run, results):
        attrs = {
            'class': 'pydocx-strike',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

    def export_run_property_strike(self, run, results):
        attrs = {
            'class': 'pydocx-strike',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

    def export_run_property_vanish(self, run, results):
        attrs = {
            'class': 'pydocx-hidden',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

    def export_run_property_hidden(self, run, results):
        attrs = {
            'class': 'pydocx-hidden',
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

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

    def export_run_property_color(self, run, results):
        if run.properties is None or run.properties.color is None:
            return results

        attrs = {
            'style': 'color:#' + run.properties.color
        }
        tag = HtmlTag('span', **attrs)
        return self.export_run_property(tag, run, results)

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

    def get_hyperlink_tag(self, target_uri):
        if target_uri:
            href = self.escape(target_uri)
            return HtmlTag('a', href=href)

    def export_hyperlink(self, hyperlink):
        results = super(PyDocXHTMLExporter, self).export_hyperlink(hyperlink)
        tag = self.get_hyperlink_tag(target_uri=hyperlink.target_uri)
        if tag:
            results = tag.apply(results, allow_empty=False)

        # Prevent underline style from applying by temporarily monkey-patching
        # the export underline function. There's got to be a better way.
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
        return HtmlTag(
            tag_name,
            allow_whitespace=True,
            allow_self_closing=True,
        )

    def export_break(self, br):
        tag = self.get_break_tag(br)
        if tag:
            yield tag

    def get_table_tag(self, table):
        return HtmlTag('table', border='1')

    def export_table(self, table):
        table_cell_spans = table.calculate_table_cell_spans()
        self.table_cell_rowspan_tracking[table] = table_cell_spans
        results = super(PyDocXHTMLExporter, self).export_table(table)
        tag = self.get_table_tag(table)
        return tag.apply(results)

    def export_table_row(self, table_row):
        results = super(PyDocXHTMLExporter, self).export_table_row(table_row)
        tag = HtmlTag('tr')
        return tag.apply(results)

    def export_table_cell(self, table_cell):
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
            parent_table = table_cell.get_first_ancestor(wordprocessing.Table)
            rowspan_counts = self.table_cell_rowspan_tracking[parent_table]
            rowspan = rowspan_counts.get(table_cell, 1)
            attrs = {}
            if colspan > 1:
                attrs['colspan'] = colspan
            if rowspan > 1:
                attrs['rowspan'] = rowspan
            tag = HtmlTag('td', **attrs)

        numbering_spans = self.yield_numbering_spans(table_cell.children)
        results = self.yield_nested_with_line_breaks_between_paragraphs(
            numbering_spans,
            self.export_node,
        )
        if tag:
            results = tag.apply(results)

        self.in_table_cell = True
        for result in results:
            yield result
        self.in_table_cell = False

    def export_drawing(self, drawing):
        length, width = drawing.get_picture_extents()
        rotate = drawing.get_picture_rotate_angle()
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
        if rotate:
            attrs['rotate'] = rotate

        tag = self.get_image_tag(image=image, **attrs)
        if tag:
            yield tag

    def get_image_source(self, image):
        if image is None:
            return
        elif uri_is_external(image.uri):
            return image.uri
        else:
            image.stream.seek(0)
            data = image.stream.read()
            _, filename = posixpath.split(image.uri)
            extension = filename.split('.')[-1].lower()
            b64_encoded_src = 'data:image/{ext};base64,{data}'.format(
                ext=extension,
                data=base64.b64encode(data).decode(),
            )
            return self.escape(b64_encoded_src)

    def get_image_tag(self, image, width=None, height=None, rotate=None):
        image_src = self.get_image_source(image)
        if image_src:
            attrs = {
                'src': image_src
            }
            if width and height:
                attrs['width'] = width
                attrs['height'] = height
            if rotate:
                attrs['style'] = 'transform: rotate(%sdeg);' % rotate

            return HtmlTag(
                'img',
                allow_self_closing=True,
                allow_whitespace=True,
                **attrs
            )

    def export_inserted_run(self, inserted_run):
        results = super(PyDocXHTMLExporter, self).export_inserted_run(inserted_run)
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
        tag = self.get_image_tag(image=image, width=width, height=height)
        if tag:
            yield tag

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
        footnote_parent = footnote_reference_mark.get_first_ancestor(
            wordprocessing.Footnote,
        )
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
        tag = HtmlTag('span', allow_whitespace=True, **attrs)
        return tag.apply(results)

    def export_numbering_span(self, numbering_span):
        results = super(PyDocXHTMLExporter, self).export_numbering_span(numbering_span)
        pydocx_class = 'pydocx-list-style-type-{fmt}'.format(
            fmt=numbering_span.numbering_level.num_format,
        )
        attrs = {}
        tag_name = 'ul'
        if not numbering_span.numbering_level.is_bullet_format():
            attrs['class'] = pydocx_class
            tag_name = 'ol'
        tag = HtmlTag(tag_name, **attrs)
        return tag.apply(results)

    def export_numbering_item(self, numbering_item):
        results = self.yield_nested_with_line_breaks_between_paragraphs(
            numbering_item.children,
            self.export_node,
        )
        tag = HtmlTag('li')
        return tag.apply(results)

    def export_field_hyperlink(self, simple_field, field_args):
        results = self.yield_nested(simple_field.children, self.export_node)
        if not field_args:
            return results
        target_uri = field_args.pop(0)
        bookmark = None
        bookmark_option = False
        for arg in field_args:
            if bookmark_option is True:
                bookmark = arg
            if arg == '\l':
                bookmark_option = True
        if bookmark_option and bookmark:
            target_uri = '{0}#{1}'.format(target_uri, bookmark)

        tag = self.get_hyperlink_tag(target_uri=target_uri)
        return tag.apply(results)
