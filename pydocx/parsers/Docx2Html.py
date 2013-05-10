from pydocx.DocxParser import DocxParser

import xml.sax.saxutils
import textwrap


class Docx2Html(DocxParser):

    @property
    def parsed(self):
        self._parsed = self._parsed.replace('<p></p><p></p>', '<br />')
        self._parsed = self._parsed.replace('</p><br /><p>', '</p><p>')
        self._parsed = self._parsed.replace('</p><br /><ul>', '</p><ul>')
        return (
            "<html>{head}<body>{content}</body></html>"
        ).format(
            head=self.head(),
            content=self._parsed,
        )

    def head(self):
        return "<head>{style}</head>".format(
            style=self.style(),
        )

    def style(self):
        return textwrap.dedent('''<style>.insert{{color:red}}.delete
        {{color:red; text-decoration:line-through}}.center
        {{text-align:center}}.right{{text-align:right}}
        .left{{text-align:left}} .comment{{color:blue}}
        body{{width:{width}px; margin:0px auto;
        }}</style>''').format(width=(self.page_width * (4 / 3)))
        #multiple by (4/3) to get to px

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
            "<span class='insert' author='{author}' "
            "date='{date}'>{text}</span>"
        ).format(author=author, date=date, text=text)

    def hyperlink(self, text, href):
        if text == '':
            return ''
        return '<a href="%(href)s">%(text)s</a>' % {
            'href': href,
            'text': text,
        }

    def image_handler(self, path):
        return path

    def image(self, path, x, y):
        src = self.image_handler(path)
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
        return '<hr>'

    def indent(self, text, just='', firstLine='', left='', right=''):
        slug = '<div'
        if just:
            slug += " class='%(just)s"
        if firstLine or left or right:
            slug += "' style ="
        if firstLine:
            slug += "'text-indent:%(firstLine)spx;"
        if left:
            slug += "'margin-left:%(left)spx;"
        if right:
            slug += "'margin-right:%(right)spx;"
        slug += "'>%(text)s</div>"
        return slug % {
            'text': text,
            'just': just,
            'firstLine': firstLine,
            'left': left,
            'right': right,
        }

    def break_tag(self):
        return '<br/>'
