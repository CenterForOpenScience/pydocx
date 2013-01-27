from abc import abstractmethod, ABCMeta
from bs4 import BeautifulSoup

class DocxParser:
    __metaclass__ = ABCMeta

    def __init__(self, document):
        self.soup = BeautifulSoup(document)
        self._parsed = ''
        self.parse()

    def parse(self):
        # TODO Convert the beautiful soup code to cElementTree
        self._parsed = ''
        for wcp in self.soup.find_all('w:p'):
            paragraph_text = ''
            for wcr in wcp.find_all('w:r'):
                text = wcr.find('w:t').text
                wcrpr = wcr.find('w:rpr')
                if wcrpr and wcrpr.find('w:i'):
                    paragraph_text += self.italics(text)
                else:
                    paragraph_text += text
            if not paragraph_text:
                self._parsed += self.linebreak()
            else:
                self._parsed += self.paragraph(paragraph_text)

    @property
    def parsed(self):
        return self._parsed

    @abstractmethod
    def linebreak(self):
        return ''

    @abstractmethod
    def paragraph(self, text):
        return text

    @abstractmethod
    def insertion(self, text, author, date):
        return text

    @abstractmethod
    def bold(self, text):
        return text

    @abstractmethod
    def italics(self, text):
        return text