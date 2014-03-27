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
        content = self._parsed
        content = "<html>%(head)s<body>%(content)s</body></html>" % {
            'head': self.head(),
            'content': content,
        }
        return unicode(content)

    def make_element(self, tag, contents='', attrs=None):
        html_attrs = convert_dictionary_to_html_attributes(attrs)
        if html_attrs:
            template = '<%(tag)s %(attrs)s>%(contents)s</%(tag)s>'
        else:
            template = '<%(tag)s>%(contents)s</%(tag)s>'
        return template % {
            'tag': tag,
            'attrs': html_attrs,
            'contents': contents,
        }

    def head(self):
        return "<head>%(style)s</head>" % {
            'style': self.style(),
        }

    def style(self):
        width = self.page_width / POINTS_PER_EM

        styles = {
            'body': {
                'width': '%.2fem' % width,
                'margin': '0px auto',
            }
        }

        result = []
        for name, definition in sorted(PYDOCX_STYLES.iteritems()):
            result.append('.pydocx-%s {%s}' % (
                name,
                convert_dictionary_to_style_fragment(definition),
            ))

        for name, definition in sorted(styles.iteritems()):
            result.append('%s {%s}' % (
                name,
                convert_dictionary_to_style_fragment(definition),
            ))

        return '<style>%s</style>' % ''.join(result)

    def escape(self, text):
        return xml.sax.saxutils.quoteattr(text)[1:-1]

    def linebreak(self, pre=None):
        return '<br />'

    def paragraph(self, text, pre=None):
        return '<p>' + text + '</p>'

    def heading(self, text, heading_value):
        return '<%(tag)s>%(text)s</%(tag)s>' % {
            'tag': heading_value,
            'text': text,
        }

    def insertion(self, text, author, date):
        return (
            "<span class='pydocx-insert'>%(text)s</span>"
        ) % {
            'author': author,
            'date': date,
            'text': text,
        }

    def hyperlink(self, text, href):
        if text == '':
            return ''
        return '<a href="%(href)s">%(text)s</a>' % {
            'href': href,
            'text': text,
        }

    def image_handler(self, image_data, filename):
        extension = filename.split('.')[-1].lower()
        b64_encoded_src = 'data:image/%s;base64,%s' % (
            extension,
            base64.b64encode(image_data),
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
        return (
            "<span class='pydocx-delete'>%(text)s</span>"
        ) % {
            'author': author,
            'date': date,
            'text': text,
        }

    def list_element(self, text):
        return "<li>%(text)s</li>" % {
            'text': text,
        }

    def ordered_list(self, text, list_style):
        return '<ol list-style-type="%(list_style)s">%(text)s</ol>' % {
            'text': text,
            'list_style': list_style,
        }

    def unordered_list(self, text):
        return "<ul>%(text)s</ul>" % {
            'text': text,
        }

    def bold(self, text):
        return '<strong>' + text + '</strong>'

    def italics(self, text):
        return '<em>' + text + '</em>'

    def underline(self, text):
        return '<span class="pydocx-underline">' + text + '</span>'

    def caps(self, text):
        return '<span class="pydocx-caps">' + text + '</span>'

    def small_caps(self, text):
        return '<span class="pydocx-small-caps">' + text + '</span>'

    def strike(self, text):
        return '<span class="pydocx-strike">' + text + '</span>'

    def hide(self, text):
        return '<span class="pydocx-hidden">' + text + '</span>'

    def superscript(self, text):
        return '<sup>%(text)s</sup>' % {
            'text': text,
        }

    def subscript(self, text):
        return '<sub>%(text)s</sub>' % {
            'text': text,
        }

    def tab(self):
        return '<span class="pydocx-tab"> </span>'

    def table(self, text):
        return '<table border="1">' + text + '</table>'

    def table_row(self, text):
        return '<tr>' + text + '</tr>'

    def table_cell(self, text, col='', row=''):
        slug = '<td'
        if col:
            slug += ' colspan="%(colspan)s"'
        if row:
            slug += ' rowspan="%(rowspan)s"'
        slug += '>%(text)s</td>'
        return slug % {
            'colspan': col,
            'rowspan': row,
            'text': text,
        }

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
            firstLine = firstLine / TWIPS_PER_POINT / POINTS_PER_EM
            style['text-indent'] = '%.2fem' % firstLine
        if left:
            left = left / TWIPS_PER_POINT / POINTS_PER_EM
            style['margin-left'] = '%.2fem' % left
        if right:
            right = right / TWIPS_PER_POINT / POINTS_PER_EM
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
