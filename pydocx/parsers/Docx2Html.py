from pydocx.DocxParser import DocxParser
from pydocx.NewDocxParser import NewDocxParser
import xml.sax.saxutils

class Docx2Html(DocxParser):

    @property
    def parsed(self):
        return '<html><head><style>.insert{color:red}</style></head><body>' + self._parsed + '</body></html>'

    def escape(self, text):
        return  xml.sax.saxutils.quoteattr(text)[1:-1]

    def linebreak(self, pre=None):
        return '<br />'

    def paragraph(self, text):
        return '<p>' + text + '</p>'

    def insertion(self, text, author, date):
        return "<span class='insert' author='{author}' date='{date}'>{text}</span>".format(author=author, date=date, text=self.escape(text))

    def list_element(self, text):
        return "<li>{text}</li>".format(text=text)

    def ordered_list(self, text):
        return '<ol>' + text + '</ol>'

    def unordered_list(self, text):
        return '<ul>' + text + '</ul>'

    def bold(self, text):
        return '<b>' + self.escape(text) + '</b>'

    def italics(self, text):
        return '<i>' + self.escape(text) + '</i>'

    def underline(self,text):
        return '<u>' + self.escape(text) + '</u>'

    def tab(self):
        return '&nbsp&nbsp&nbsp&nbsp' #### insert before the text right?? so got the text and just do an insert at the beginning!