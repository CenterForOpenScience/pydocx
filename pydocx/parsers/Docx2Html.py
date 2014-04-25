from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
import xml.sax.saxutils

from pydocx.DocxParser import DocxParser, TWIPS_PER_POINT
from pydocx.utils import (
    convert_dictionary_to_html_attributes,
    convert_dictionary_to_style_fragment,
)

POINTS_PER_EM = 12

PYDOCX_STYLES = {
    'insert': {
        'color': 'green',
    },
    'delete': {
        'color': 'red',
        'text-decoration': 'line-through',
    },
    'center': {
        'text-align': 'center',
    },
    'right': {
        'text-align': 'right',
    },
    'left': {
        'text-align': 'left',
    },
    'comment': {
        'color': 'blue',
    },
    'underline': {
        'text-decoration': 'underline',
    },
    'caps': {
        'text-transform': 'uppercase',
    },
    'small-caps': {
        'font-variant': 'small-caps',
    },
    'strike': {
        'text-decoration': 'line-through',
    },
    'hidden': {
        'visibility': 'hidden',
    },
    'tab': {
        'display': 'inline-block',
        'width': '4em',
    },
}


class Docx2Html(DocxParser):

    @property
    def parsed(self):
        content = super(Docx2Html, self).parsed
        content = "<html>%(head)s<body>%(content)s</body></html>" % {
            'head': self.head(),
            'content': content,
        }
        return content

    def make_element(self, tag, contents='', attrs=None):
        if attrs:
            attrs = convert_dictionary_to_html_attributes(attrs)
            template = '<%(tag)s %(attrs)s>%(contents)s</%(tag)s>'
        else:
            template = '<%(tag)s>%(contents)s</%(tag)s>'
        return template % {
            'tag': tag,
            'attrs': attrs,
            'contents': contents,
        }

    def head(self):
        return self.make_element(
            tag='head',
            contents=self.style(),
        )

    def style(self):
        width = self.page_width / POINTS_PER_EM

        styles = {
            'body': {
                'width': '%.2fem' % width,
                'margin': '0px auto',
            }
        }

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

    def image_handler(self, image_data, filename):
        extension = filename.split('.')[-1].lower()
        b64_encoded_src = 'data:image/%s;base64,%s' % (
            extension,
            base64.b64encode(image_data).decode(),
        )
        b64_encoded_src = self.escape(b64_encoded_src)
        return b64_encoded_src

    def image(self, image_data, filename, x, y):
        src = self.image_handler(image_data, filename)
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
