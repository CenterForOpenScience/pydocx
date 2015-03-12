from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import xml.sax.saxutils

from pydocx.constants import (
    POINTS_PER_EM,
    PYDOCX_STYLES,
    TWIPS_PER_POINT,
)
from pydocx.DocxParser import DocxParser
from pydocx.util.xml import (
    convert_dictionary_to_html_attributes,
    convert_dictionary_to_style_fragment,
)


class Docx2Html(DocxParser):

    @property
    def parsed(self):
        content = super(Docx2Html, self).parsed
        content = '<html>{header}<body>{body}{footer}</body></html>'.format(
            header=self.head(),
            body=content,
            footer=self.footer(),
        )
        return content

    @property
    def parsed_content(self):
        return super(Docx2Html, self).parsed

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

    def heading(self, text, heading_value):
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
        return self.make_element(
            tag='ol',
            contents=text,
            attrs={
                'list-style-type': list_style,
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
        >>> parser = Docx2Html('foo')
        >>> parser._convert_measurement(30)
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
