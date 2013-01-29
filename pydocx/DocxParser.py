from abc import abstractmethod, ABCMeta
from bs4 import BeautifulSoup

class DocxParser:
    __metaclass__ = ABCMeta

    def __init__(self, document):
        self.soup = BeautifulSoup(document)
        self._parsed = ''
        self.parse()

    def _inside(self, el):
        pass

    def parse(self):
        # TODO Convert the beautiful soup code to cElementTree
        self._parsed = ''
        for wcp in self.soup.find_all('w:p'):
            paragraph_text = ''
            print wcp
            for wcr in wcp.find_all('w:r'):
                run_text = ''
                text = ''
                text = wcr.find('w:t').text if wcr.find('w:t') else ''
                # Inner text dealings

                wcrpr = wcr.find('w:rpr')
                if wcrpr and wcrpr.find('w:i'):
                    run_text += self.italics(text)
                if wcrpr and wcrpr.find('w:b'):
                    run_text += self.bold(text)
                if wcrpr and wcrpr.find('w:u'):
                    run_text += self.underline(text)

                if not run_text:
                    # TODO escape(text)
                    run_text = text

                # Outside applies to text

                if wcr.find('w:tab'):
                    run_text = self.tab() + run_text

                if wcr.parent.find('w:ilvl'):
                    run_text = self.list_element(run_text)

                wcins = wcr.find_parent('w:ins')
                if wcins:
                    author = wcins['w:author']
                    date = wcins['w:date']
                    run_text = self.insertion(run_text, author, date)
                paragraph_text += run_text
            if not paragraph_text:
                self._parsed += self.linebreak()
            else:
                self._parsed += self.paragraph(paragraph_text)


#            for wcr in wcp.find_all('w:r'):
#
#                wcrpr = wcr.find('w:rpr')
#
#                if wcrpr and wcrpr.find('w:b') and not wcp.find('w:ins'):
#                    paragraph_text+=self.bold(text)
#                if wcrpr and wcrpr.find('w:u') and not wcp.find('w:ins'):
#                    paragraph_text+=self.underline(text)
#                if wcp and wcp.find('w:ins'):
#                    author=''
#                    date=''
#                    for ins in wcp.find_all('w:ins'):
#                        author= ins['w:author']
#                        date=ins['w:date']
#                        if ins.find('w:t'):
#                            text=ins.find('w:t').text
#                            try:
#                                paragraph_text+=self.insertion(text,author,date)
#                            except:
#                                pass
#                        else:
#                            self._parsed+=self.linebreak()
#                elif not (wcrpr and wcrpr.find('w:i') or wcrpr and wcrpr.find('w:b') or wcrpr and wcrpr.find('w:u') or wcp and wcp.find('w:ins') ):
#                    paragraph_text += text
#            if not paragraph_text:
#                self._parsed += self.linebreak()
#            else:
#                self._parsed += self.paragraph(paragraph_text)

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

    @abstractmethod
    def underline(self,text):
        return text

    @abstractmethod
    def tab(self):
        return True

#    @abstractmethod
#    def ordered_list(self, text):
#        pass
#
#    @abstractmethod
#    def definition_list(self, text):
#        pass
#
#    @abstractmethod
#    def unordered_list(self, text):
#         pass

    @abstractmethod
    def list_element(self,text):
        return text