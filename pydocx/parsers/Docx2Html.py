from pydocx.DocxParser import DocxParser

import xml.sax.saxutils

class Docx2Html(DocxParser):

    @property
    def parsed(self):
        self._parsed = self._parsed.replace('<p></p><p></p>', '<br />')
        self._parsed = self._parsed.replace('</p><br /><p>', '</p><p>')
        self._parsed = self._parsed.replace('</p><br /><ul>', '</p><ul>')
        return '<html><head><style>.insert{{color:red}}.delete{{color:red; text-decoration:line-through}}</style></head><body>{}</body></html>'.format(self._parsed)

    def escape(self, text):
        return  xml.sax.saxutils.quoteattr(text)[1:-1]

    def linebreak(self, pre=None):
        return '<br />'

    def paragraph(self, text, pre=None):
        return '<p>' + text + '</p>'

    def insertion(self, text, author, date):
        return "<span class='insert' author='{author}' date='{date}'>{text}</span>".format(author=author, date=date, text=text)

    def deletion(self, text, author, date):
        return "<span class='delete' author='{author}' date='{date}'>{text}</span>".format(author=author, date=date, text=text)

    def list_element(self, text):
        return "<li>{text}</li>".format(text=text)

    def ordered_list(self, text):
        return "<ol>{text}</ol>".format(text=text)

    def unordered_list(self, text):
        return "<ul>{text}</ul>".format(text=text)

    def bold(self, text):
        return '<b>' + text + '</b>'

    def italics(self, text):
        return '<i>' + text + '</i>'

    def underline(self,text):
        return '<u>' + text + '</u>'

    def tab(self):
        return '&nbsp&nbsp&nbsp&nbsp' #### insert before the text right?? so got the text and just do an insert at the beginning!