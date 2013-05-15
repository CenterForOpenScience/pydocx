__author__ = 'samportnow'

from .tests import document_builder
from pydocx.DocxParser import ElementTree


class converter():

    def __init__(self, html):
        self.html = ElementTree.fromstring(html)
        self.build()

    def build(self):
        def add_parent(el):
            for child in el.getchildren():
                setattr(child, 'parent', el)
                add_parent(child)
        add_parent(self.html)
        self.set_list_attributes()
        self.parse(self.html.find_first('body'))

    def find_all_by_tags(self, html, *args):
        list_elements = []
        for el in html.iter():
            if el.tag in args:
                list_elements.append(el)
        return list_elements

    def check_for_lst_parent(self, el):
        lst_parent = False
        if el.parent.tag != 'body':
            if el.parent.tag == 'ol' or el.parent.tag == 'ul':
                lst_parent = True
            self.check_for_lst_parent(el.parent)
        else:
            return lst_parent

    def set_list_attributes(self):
        ilvl = 0
        numId = -1
        lsts = self.find_all_by_tags(self.html, 'ol', 'ul')
        for lst in lsts:
            lst.getchildren()[0].is_first_list_item = True
            lst.getchildren()[-1].is_last_list_item = True
        for el in self.html.find_first('body').iter():
            if el.tag == 'li':
                if self.check_for_lst_parent(el.parent) \
                   is False and el.is_first_list_item is True:
                    numId += 1
                    ilvl = 0
                if el.is_first_list_item is True:
                    ilvl += 1
                el.ilvl = ilvl
                el.num_id = numId

    def parse(self, el):
        for child in el.getchildren():
                parsed = ''
                self.parse(child)
                if child.tag == 'b':
                    self.bold = True
                else:
                    self.bold = False
                if child.tag == 'i':
                    pass
                if child.tag == 'u':
                    pass
                if child.tag == 'li':
                    parsed = document_builder.DocxBuilder.li(
                        child.text, child.ilvl, child.num_id, self.bold)
                if child.tag == 'p':
                    parsed = document_builder.DocxBuilder.p_tag(
                        child.text, self.bold)
                return parsed
