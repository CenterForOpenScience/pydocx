from abc import abstractmethod, ABCMeta
import zipfile
import logging
import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("NewParser")

def remove_namespaces(document):
    root = ElementTree.fromstring(document)
    for child in root.iter():
        child.tag = child.tag.split("}")[1]
        child.attrib = {k.split("}")[1]:v for k,v in child.attrib.items()}
    return ElementTree.tostring(root)

# Add some helper functions to Element to make it slightly more readable

def has_child(self, tag):
    return True if self.find(tag) is not None else False

def has_child_all(self, tag):
    return True if self.find('.//' + tag) is not None else False

def find_all(self, tag):
    return self.find('.//' + tag)

def findall_all(self, tag):
    return self.findall('.//' + tag)

setattr(Element, 'has_child', has_child)
setattr(Element, 'has_child_all', has_child_all)
setattr(Element, 'find_all', find_all)
setattr(Element, 'findall_all', findall_all)

# End helpers

class DocxParser:
    __metaclass__ = ABCMeta

    def __init__(self, path):
        self._parsed = ''
        self.in_list = False

        document = ''
        with zipfile.ZipFile(path) as f:
            document = f.read('word/document.xml')
            try:
                numbering= f.read('word/numbering.xml')
            except:
                pass

        self.root = ElementTree.fromstring(remove_namespaces(document))
        print self.root.findall_all('commentReference') #can find this, but has no children?

        try:
            self.numbering_root = ElementTree.fromstring(remove_namespaces(numbering))
        except:
            pass
        self.parse_begin(self.root)

    def parse_begin(self, el):
        self._parsed += self.parse_lists(el)

    def parse_lists(self, el):
        parsed = ''

        p_list = el.findall_all('p')

        list_started = False
        list_type = ''
        list_chunks = []
        index_start = 0
        index_end = 1
        for i, el in enumerate(p_list):
            if not list_started and el.has_child_all('ilvl'):
                list_started = True
                list_type = self.get_list_style(el.find_all('numId').attrib['val'])
                list_chunks.append(p_list[index_start:index_end])
                index_start = i
                index_end = i+1
            elif list_started and el.has_child_all('ilvl') and not list_type == self.get_list_style(el.find_all('numId').attrib['val']):
                list_type = self.get_list_style(el.find_all('numId').attrib['val'])
                list_started = True
                list_chunks.append(p_list[index_start:index_end])
                index_start = i
                index_end = i+1
            elif list_started and not el.has_child_all('ilvl'):
                list_started = False
                list_chunks.append(p_list[index_start:index_end])
                index_start = i
                index_end = i+1
            else:
                index_end = i+1
        list_chunks.append(p_list[index_start:index_end])
        for chunk in list_chunks:
            chunk_parsed = ''
            for el in chunk:
                chunk_parsed += self.parse(el)
            if chunk[0].has_child_all('ilvl'):
                lst_style = self.get_list_style(chunk[0].find_all('numId').attrib['val'])
                if lst_style['val'] == 'bullet':
                    parsed += self.unordered_list(chunk_parsed)
                else:
                    parsed += self.ordered_list(chunk_parsed)
            else:
                parsed += chunk_parsed

        return parsed

    def parse(self, el):
        parsed = ''
        for child in el:
            parsed += self.parse(child)

        if el.tag == 'ilvl':
            self.in_list = True
            ## This starts the returns
        if el.tag == 'r':
            return self.parse_r(el)
        elif el.tag == 'p':
            return self.parse_p(el, parsed)
        elif el.tag == 'ins':
            return self.insertion(parsed, '', '')
        else:
            return parsed

    def parse_p(self, el, text):
        parsed = text
        if self.in_list:
            self.in_list = False
            parsed = self.list_element(parsed)
        elif not el.has_child_all('t'):
            parsed = self.linebreak()
        else:
            parsed = self.paragraph(parsed)
        return parsed

    def parse_r(self, el):
        is_deleted = False
        text = None
        if el.has_child('t'):
            text = self.escape(el.find('t').text)
        elif el.has_child('delText'):
            text = self.escape(el.find('delText').text)
            is_deleted = True
        if text:
            rpr = el.find('rPr')
            if rpr is not None:
                fns = []
                if rpr.has_child('b'):
                    fns.append(self.bold)
                if rpr.has_child('i'):
                    fns.append(self.italics)
                if rpr.has_child('u'):
                    fns.append(self.underline)
                for fn in fns:
                    text = fn(text)
            if is_deleted:
                text = self.deletion(text,'','')
            return text
        else:
            return ''

    def get_list_style(self, numval):

        ids = self.numbering_root.findall_all('num')
        for id in ids:
            if id.attrib['numId'] == numval:
                abstractid=id.find('abstractNumId')
                abstractid=abstractid.attrib['val']
                style_information=self.numbering_root.findall_all('abstractNum')
                for info in style_information:
                    if info.attrib['abstractNumId'] == abstractid:
                        for i in info.iter():
                            if i.find('numFmt') is not None:
                                return i.find('numFmt').attrib



    @property
    def parsed(self):
        return self._parsed

    @property
    def escape(self, text):
        return text

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
    def deletion(self, text, author, date):
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

