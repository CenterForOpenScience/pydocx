# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import xml.sax.saxutils
from itertools import chain
from collections import defaultdict

from pydocx.constants import (
    POINTS_PER_EM,
    PYDOCX_STYLES,
    TWIPS_PER_POINT,
)
from pydocx.export.base import PyDocXExporter, OldPyDocXExporter
from pydocx.openxml import wordprocessing
from pydocx.util.xml import (
    convert_dictionary_to_html_attributes,
    convert_dictionary_to_style_fragment,
)


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
            self.attrs.items()
        )


class PyDocXHTMLExporter(PyDocXExporter):
    def __init__(self, *args, **kwargs):
        super(PyDocXHTMLExporter, self).__init__(*args, **kwargs)
        self.numbering_tracking = {}
        self.numbering_is_active = False

    def head(self):
        tag = HtmlTag('head')
        results = chain(self.meta(), self.style())
        return tag.apply(results)

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
        numbering = self.numbering_definitions_part.numbering
        numbering_tracking = defaultdict(dict)

        previous_num_def = None
        previous_paragraph = None
        previous_num_def_paragraph = None
        levels = []

        # * If this is the final list item for the def, close the def
        # * If this is the first list item for the def, open the def
        # * If the def = prev and level = prev,
        # then close the list item and open a new one
        # * If the def = prev, and level + prev,
        # then open a new list, open a new list item
        # * If the def = prev, and level - prev,
        # then close the previous level
        for paragraph in paragraphs:
            num_def = paragraph.get_numbering_definition(numbering)
            if num_def is not None:
                level = paragraph.get_numbering_level(numbering)
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
                        # This level is less than the previous level, so close
                        # the previous level
                        numbering_tracking[paragraph]['close-level'] = [levels.pop()]  # noqa
                elif previous_num_def is None:
                    # There hasn't been a previous numbering definition
                    numbering_tracking[paragraph]['open-level'] = level
                    levels.append(level)
                else:
                    # There was a previous numbering definition. Close all of
                    # the levels and open the new definition
                    assert previous_paragraph
                    numbering_tracking[previous_paragraph]['close-level'] = levels  # noqa
                    numbering_tracking[paragraph]['open-level'] = level
                    levels = [level]

                previous_num_def = num_def
                previous_num_def_paragraph = paragraph
            previous_paragraph = paragraph

        if previous_num_def is not None:
            # Finialize the previous numbering definition if it exists
            assert previous_num_def_paragraph
            numbering_tracking[previous_num_def_paragraph]['close-level'] = levels  # noqa

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
            raise StopIteration

        tracking = numbering_tracking.get(paragraph)
        if not tracking:
            raise StopIteration

        return tracking

    def export_numbering_level_begin(self, paragraph):
        numbering = self.numbering_definitions_part.numbering

        num_def = paragraph.get_numbering_definition(numbering)
        if not num_def:
            raise StopIteration

        tracking = self.get_numbering_tracking(paragraph)

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
            self.numbering_is_active = True
            yield li
        raise StopIteration

    def export_numbering_level_end(self, paragraph):
        numbering = self.numbering_definitions_part.numbering

        num_def = paragraph.get_numbering_definition(numbering)
        if not num_def:
            raise StopIteration

        tracking = self.get_numbering_tracking(paragraph)

        levels = tracking.get('close-level', [])
        for level in reversed(levels):
            yield HtmlTag('li', closed=True)
            # TODO only end numbering on the final numbering paragraph
            self.numbering_is_active = False
            if self._is_ordered_list(level):
                yield HtmlTag('ol', closed=True)
            else:
                yield HtmlTag('ul', closed=True)
        raise StopIteration

    def get_paragraph_tag(self, paragraph):
        if not self.numbering_is_active:
            return HtmlTag('p')

    def export_paragraph(self, paragraph):
        for result in self.export_numbering_level_begin(paragraph):
            yield result

        results = super(PyDocXHTMLExporter, self).export_paragraph(paragraph)
        tag = self.get_paragraph_tag(paragraph)
        if tag:
            results = tag.apply(results, allow_empty=False)

        for result in results:
            yield result

        for result in self.export_numbering_level_end(paragraph):
            yield result

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
            'class': 'pydocx-dstrike',
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
        align = run.properties.vertical_align
        if align == 'superscript':
            tag = HtmlTag('sup')
        elif align == 'subscript':
            tag = HtmlTag('sub')
        else:
            return results
        return tag.apply(results)

    def export_text(self, text):
        results = super(PyDocXHTMLExporter, self).export_text(text)
        for result in results:
            if result:
                yield result

    def export_break(self, br):
        if br.is_page_break():
            tag_name = 'hr'
        else:
            tag_name = 'br'
        yield HtmlTag(tag_name, allow_self_closing=True)


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

    def _convert_measurement(self, value):
        '''
        >>> exporter = PyDocXHTMLExporter('foo')
        >>> exporter._convert_measurement(30)
        0.125
        '''
        return value / TWIPS_PER_POINT / POINTS_PER_EM

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
            firstLine = self._convert_measurement(firstLine)
            style['text-indent'] = '%.2fem' % firstLine
        if left:
            left = self._convert_measurement(left)
            style['margin-left'] = '%.2fem' % left
        if right:
            right = self._convert_measurement(right)
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
