from abc import abstractmethod, ABCMeta
import zipfile
import logging
import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import _ElementInterface

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("NewParser")


def remove_namespaces(document):
    root = ElementTree.fromstring(document)
    for child in el_iter(root):
        child.tag = child.tag.split("}")[1]
        child.attrib = dict(
            (k.split("}")[1], v)
            for k, v in child.attrib.items()
        )
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


def el_iter(el):
    try:
        return el.iter()
    except AttributeError:
        return el.findall('.//*')


setattr(_ElementInterface, 'has_child', has_child)
setattr(_ElementInterface, 'has_child_all', has_child_all)
setattr(_ElementInterface, 'find_all', find_all)
setattr(_ElementInterface, 'findall_all', findall_all)
setattr(_ElementInterface, 'parent', None)
setattr(_ElementInterface, 'parent_list', [])

# End helpers


class DocxParser:
    __metaclass__ = ABCMeta

    def __init__(self, path):
        self._parsed = ''
        self.in_list = False

        f = zipfile.ZipFile(path)
        try:
            self.document_text = f.read('word/document.xml')
            try:
                self.numbering_text = f.read('word/numbering.xml')
            except KeyError:
                pass
            try:
                self.comment_text = f.read('word/comments.xml')
            except KeyError:
                pass
        finally:
            f.close()

        self.root = ElementTree.fromstring(
            remove_namespaces(self.document_text),
        )

        def add_parent(el):
            for child in el.getchildren():
                setattr(child, 'parent', el)
                add_parent(child)
        add_parent(self.root)

        def create_parent_list(el, tmp=None):
            if tmp is None:
                tmp = []
            for child in el:
                tmp.append(el)
                tmp = create_parent_list(child, tmp)
            el.parent_list = tmp[:]
            try:
                tmp.pop()
            except:
                tmp = []
            return tmp

        create_parent_list(self.root)

        self.comment_store = None
        self.numbering_store = None
        self.ignore_current = False
        self.elements = []
        self.tables_seen = []
        self.visited = []
        try:
            self.numbering_root = ElementTree.fromstring(
                remove_namespaces(self.numbering_text),
            )
        except:
            pass
        self.parse_begin(self.root)

    def parse_begin(self, el):
        self._parsed += self.parse_lists(el)

### parse table function and is_table flag
    def parse_lists(self, el):
        parsed = ''
        first_p = el.find_all('p')
        children = []
        for child in first_p.parent:
            if child.tag == 'p' or child.tag == 'tbl':
                children.append(child)
        p_list = children
        list_started = False
        list_type = ''
        list_chunks = []
        index_start = 0
        index_end = 1
        for i, el in enumerate(p_list):
            if not list_started and el.has_child_all('ilvl'):
                list_started = True
                list_type = self.get_list_style(
                    el.find_all('numId').attrib['val'],
                )
                list_chunks.append(p_list[index_start:index_end])
                index_start = i
                index_end = i+1
            elif (
                    list_started and
                    el.has_child_all('ilvl') and
                    not list_type == self.get_list_style(
                        el.find_all('numId').attrib['val']
                    )):
                list_type = self.get_list_style(
                    el.find_all('numId').attrib['val'],
                )
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
                lst_style = self.get_list_style(
                    chunk[0].find_all('numId').attrib['val'],
                )
                if lst_style['val'] == 'bullet':
                    parsed += self.unordered_list(chunk_parsed)
                else:
                    parsed += self.ordered_list(chunk_parsed, lst_style['val'])
            elif chunk[0].has_child_all('br'):
                parsed += self.page_break()
            else:
                parsed += chunk_parsed

        return parsed

    def parse(self, el):
        parsed = ''
        if not self.ignore_current:
            tmp_d = dict(
                (tmpel.tag, i)
                for i, tmpel in enumerate(el.parent_list)
            )
            if (
                    'tbl' in tmp_d and
                    el.parent_list[tmp_d['tbl']] not in self.tables_seen):
                self.ignore_current = True
                self.tables_seen.append(el.parent_list[tmp_d['tbl']])
                tmpout = self.table(self.parse(el.parent_list[tmp_d['tbl']]))
                self.ignore_current = False
                return tmpout

        for child in el:
            parsed += self.parse(child)

        if el.tag == 'br' and el.attrib.get('type') == 'page':
            #TODO figure out what parsed is getting overwritten
            return self.page_break()
        # add it to the list so we don't repeat!
        if el.tag == 'ilvl' and el not in self.visited:
            self.in_list = True
            self.visited.append(el)
            ## This starts the returns
        elif el.tag == 'tr':
            return self.table_row(parsed)
        elif el.tag == 'tc':
            self.elements.append(el)
            return self.table_cell(parsed)
        if el.tag == 'r' and el not in self.elements:
            self.elements.append(el)
            return self.parse_r(el)
        elif el.tag == 'p':
            if el.parent.tag == 'tc':
                return parsed
            return self.parse_p(el, parsed)
        elif el.tag == 'ins':
            return self.insertion(parsed, '', '')
        else:
            return parsed

    def parse_p(self, el, text):
        if text == '':
            return ''
        parsed = text
        if self.in_list:
            self.in_list = False
            parsed = self.list_element(parsed)
        elif el.parent not in self.elements:
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
            ppr = el.parent.find('pPr')
            if ppr is not None:
                jc = ppr.find('jc')
                if jc is not None:
                    if jc.attrib['val'] == 'right':
                        text = self.right_justify(text)
                    if jc.attrib['val'] == 'center':
                        text = self.center_justify(text)
                ind = ppr.find('ind')
                if ind is not None:
                    right = None
                    left = None
                    firstLine = None
                    if 'right' in ind.attrib:
                        right = ind.attrib['right']
                        right = int(right)/20
                        right = str(right)
                    if 'left' in ind.attrib:
                        left = ind.attrib['left']
                        left = int(left)/20
                        left = str(left)
                    if 'firstLine' in ind.attrib:
                        firstLine = ind.attrib['firstLine']
                        firstLine = int(firstLine)/20
                        firstLine = str(firstLine)
                    text = self.indent(text, right, left, firstLine)
            if is_deleted:
                text = self.deletion(text, '', '')
            return text
        else:
            return ''

    def get_list_style(self, numval):
        ids = self.numbering_root.findall_all('num')
        for _id in ids:
            if _id.attrib['numId'] == numval:
                abstractid = _id.find('abstractNumId')
                abstractid = abstractid.attrib['val']
                style_information = self.numbering_root.findall_all(
                    'abstractNum',
                )
                for info in style_information:
                    if info.attrib['abstractNumId'] == abstractid:
                        for i in el_iter(info):
                            if i.find('numFmt') is not None:
                                return i.find('numFmt').attrib

    def get_comments(self, doc_id):
        if self.comment_store is None:
            # TODO throw appropriate error
            comment_root = ElementTree.fromstring(
                remove_namespaces(self.comment_text),
            )
            ids_and_info = {}
            ids = comment_root.findall_all('comment')
            for _id in ids:
                ids_and_info[_id.attrib['id']] = {
                    "author": _id.attrib['author'],
                    "date": _id.attrib['date'],
                    "text": _id.findall_all('t')[0].text,
                }
            self.comment_store = ids_and_info
        return self.comment_store[doc_id]

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
    def underline(self, text):
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
    def list_element(self, text):
        return text

    @abstractmethod
    def table(self, text):
        return text

    @abstractmethod
    def table_row(self, text):
        return text

    @abstractmethod
    def table_cell(self, text):
        return text

    @abstractmethod
    def page_break(self):
        return True

    @abstractmethod
    def right_justify(self, text):
        return text

    @abstractmethod
    def center_justify(self, text):
        return text

    @abstractmethod
    def indent(self, text, left=None, right=None, firstLine=None):
        return text

    #TODO JUSTIFIED JUSTIFIED TEXT
