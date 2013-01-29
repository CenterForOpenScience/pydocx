from pydocx.DocxParser import DocxParser
import xml.sax.saxutils

class Docx2Html(DocxParser):

    @property
    def parsed(self):
        return '<html><head></head><body>' + self._parsed + '</body></html>'

    def escape(self, text):
        return  xml.sax.saxutils.quoteattr(text)

    def linebreak(self):
        return '<br />'

    def paragraph(self, text):
        return '<p>' + text + '</p>'

    def insertion(self, text, author, date):
        return "<div class='insert>" + text + "</div>"

    def bold(self, text):
        return '<b>' + self.escape(text) + '</b>'

    def italics(self, text):
        return '<i>' + self.escape(text) + '</i>'

    def underline(self,text):
        return '<u>' + self.escape(text) + '</u>'