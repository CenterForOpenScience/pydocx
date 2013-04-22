from pydocx.DocxParser import DocxParser

import xml.sax.saxutils


class Docx2Html(DocxParser):

    @property
    def parsed(self):
        self._parsed = self._parsed.replace('<p></p><p></p>', '<br />')
        self._parsed = self._parsed.replace('</p><br /><p>', '</p><p>')
        self._parsed = self._parsed.replace('</p><br /><ul>', '</p><ul>')
        return (
            '<html>{head}<body>{content}</body></html>'
        ).format(
            head=self.head(),
            content=self._parsed,
        )

    def head(self):
        return '<head>{style}</head>'.format(
            style=self.style(),
        )

    def style(self):
        return '<style>.insert{{color:red}}.delete'
        '{{color:red; text-decoration:line-through}}.center'
        '{{text-align:center}}.right{{text-align:right}}</style>'

    def escape(self, text):
        return xml.sax.saxutils.quoteattr(text)[1:-1]

    def linebreak(self, pre=None):
        return '<br />'

    def paragraph(self, text, pre=None):
        return '<p>' + text + '</p>'

    def insertion(self, text, author, date):
        return (
            "<span class='insert' author='{author}' "
            "date='{date}'>{text}</span>"
        ).format(author=author, date=date, text=text)

    def hyperlink(self, text, href):
        return '<a href="%(href)s">%(text)s</a>' % {
            'href': href,
            'text': text,
        }

    def deletion(self, text, author, date):
        return (
            "<span class='delete' author='{author}' "
            "date='{date}'>{text}</span>"
        ).format(author=author, date=date, text=text)

    def list_element(self, text):
        return "<li>{text}</li>".format(text=text)

    def ordered_list(self, text, list_style):
        return "<ol>{text}</ol>".format(text=text)

    def unordered_list(self, text):
        return "<ul>{text}</ul>".format(text=text)

    def bold(self, text):
        return '<b>' + text + '</b>'

    def italics(self, text):
        return '<i>' + text + '</i>'

    def underline(self, text):
        return '<u>' + text + '</u>'

    def tab(self):
        # Insert before the text right?? So got the text and just do an insert
        # at the beginning!
        return '&nbsp&nbsp&nbsp&nbsp'

    def table(self, text):
        return '<table border=1>' + text + '</table>'

    def table_row(self, text):
        return '<tr>' + text + '</tr>'

    def table_cell(self, text):
        return '<td>' + text + '</td>'

    def page_break(self):
        return '<hr>'

    def center_justify(self, text):
        return "<div class = 'center'>" + text + '</div>'

    def right_justify(self, text):
        return "<div class = 'right'>" + text + '</div>'

    def indent(self, text, right, left, firstLine):
        return "<div style = 'margin-left:{left}pt'>{text}</div>".format(
            left=left,
            text=text,
        )
