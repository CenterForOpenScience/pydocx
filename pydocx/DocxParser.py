from abc import abstractmethod, ABCMeta
from bs4 import BeautifulSoup
import zipfile

class DocxParser:
    __metaclass__ = ABCMeta

    def __init__(self, path):
        document = None
        with zipfile.ZipFile(path) as f:
            document = f.read('word/document.xml')
            numbering= f.read('word/numbering.xml')
        self.document = BeautifulSoup(document)
        self.numbering = BeautifulSoup(numbering)
        self._parsed = ''
        self.parse()

    def _inside(self, el):
        pass

    def parse(self):
        # TODO Convert the beautiful soup code to cElementTree
        self._parsed = ''
        list_started_flag = False
        list_text = ''
        for wcp in self.document.find_all('w:p'):
            paragraph_text = ''
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

                wcilvl = wcp.find('w:ilvl')
                if wcilvl and not wcr.find('w:rpr'):
                    list_started_flag = True
                    type_of_lst=self.get_lst_style(wcilvl)
                    run_text = self.list_element(run_text)
                wcins = wcr.find_parent('w:ins')
                if wcins:
                    author = wcins['w:author']
                    date = wcins['w:date']
                    run_text = self.insertion(run_text, author, date)
                paragraph_text += run_text
            #if you are in a list, if sibling is not the same and

            is_wcp_a_list = True if wcp.find('w:ilvl') else False
            wcp_list = wcp.find('w:ilvl')
            if not list_started_flag:
                if not paragraph_text:
                    self._parsed += self.linebreak()
                else:
                    self._parsed += self.paragraph(paragraph_text)
            else:
                if is_wcp_a_list:
                    if wcp.nextSibling:
                        is_sibling_is_list = wcp.nextSibling.find('w:ilvl')
                        if is_sibling_is_list:
                            is_sibling_list_same_type = self.get_lst_style(wcp.nextSibling.find('w:ilvl')) == self.get_lst_style(wcp_list)
                        if not is_sibling_is_list or not is_sibling_list_same_type:
                            list_text += paragraph_text
                            if type_of_lst=='bullet':
                                self._parsed += self.unordered_list(list_text)
                            else:
                                self._parsed += self.ordered_list(list_text)
                            list_started_flag = False
                            list_text = ''
                        else:
                            list_text += paragraph_text
                    else:
                        print type_of_lst
                        list_text += paragraph_text
                        if type_of_lst=='bullet':
                            self._parsed += self.unordered_list(list_text)
                        else:
                            self._parsed += self.ordered_list(list_text)

                        list_started_flag = False
                        list_text = ''

                # you're still in a list, the next one is not a list or the next one is a different type
                # you're still in a list, the next one is a list, and the next is not of a different type


    def get_lst_style(self,wcilvl):
        lvl=wcilvl.parent.find('w:numid')['w:val']
        numid=self.numbering.findAll('w:num')
        for id in numid:
            if id['w:numid']==lvl:
                abstractid=id.find('w:abstractnumid')['w:val']
                style_information=self.numbering.findAll("w:abstractnum",{"w:abstractnumid":abstractid})
                type_of_lst=style_information[0].find('w:numfmt')['w:val']
                return type_of_lst
        #return style and maybe? indent
        # if decminal, put a ul around it
            #marker=wcp.parent['w:ilvl':val]
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

    @abstractmethod
    def ordered_list(self, text):
        return text

    @abstractmethod
    def unordered_list(self, text):
         return text

    @abstractmethod
    def list_element(self,text):
        return text