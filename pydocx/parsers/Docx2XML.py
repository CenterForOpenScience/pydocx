__author__ = 'samportnow'

from pydocx.parsers.Docx2Html import Docx2Html


class Docx2XML(Docx2Html):

    def insertion(self, text, author, date):
        return ("<insertion author='{author}' "
                "date='{date}'>{text}</insertion>"
                ).format(author=author, date=date, text=text)

    def deletion(self, text, author, date):
        return ("<deletion author='{author}' "
                "date='{date}'>{text}</deletion>"
                ).format(author=author, date=date, text=text)
