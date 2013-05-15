__author__ = 'samportnow'

import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import _ElementInterface
from .tests import document_builder

def has_child(self, tag):
    """
    Determine if current element has a child. Stop at first child.
    """
    return True if self.find(tag) is not None else False


def has_descendant_with_tag(self, tag):
    """
    Determine if there is a child ahead in the element tree.
    """
    # Get child. stop at first child.
    return True if self.find('.//' + tag) is not None else False


def find_first(self, tag):
    """
    Find the first occurrence of a tag beneath the current element.
    """
    return self.find('.//' + tag)


def find_all(self, tag):
    """
    Find all occurrences of a tag
    """
    return self.findall('.//' + tag)


def el_iter(el):
    """
    Go through all elements
    """
    try:
        return el.iter()
    except AttributeError:
        return el.findall('.//*')


def find_ancestor_with_tag(self, tag):
    """
    Find the first ancestor with that is a `tag`.
    """
    el = self
    while el.parent:
        el = el.parent
        if el.tag == tag:
            return el
    return None

setattr(_ElementInterface, 'find_all', find_all)
setattr(_ElementInterface, 'has_child', has_child)
setattr(_ElementInterface, 'has_descendant_with_tag', has_descendant_with_tag)
setattr(_ElementInterface, 'find_first', find_first)
setattr(_ElementInterface, 'find_all', find_all)
setattr(_ElementInterface, 'find_ancestor_with_tag', find_ancestor_with_tag)
setattr(_ElementInterface, 'parent', None)
setattr(_ElementInterface, 'is_first_list_item', False)
setattr(_ElementInterface, 'is_last_list_item', False)
setattr(_ElementInterface, 'is_last_list_item_in_root', False)
setattr(_ElementInterface, 'is_list_item', False)
setattr(_ElementInterface, 'ilvl', None)
setattr(_ElementInterface, 'num_id', None)
setattr(_ElementInterface, 'heading_level', None)
setattr(_ElementInterface, 'is_in_table', False)
setattr(_ElementInterface, 'previous', None)
setattr(_ElementInterface, 'next', None)
setattr(_ElementInterface, 'row_index', None)
setattr(_ElementInterface, 'column_index', None)
setattr(_ElementInterface, 'is_last_text', False)


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


    def find_all_two(self, tag1, tag2, html):
        list_elements = []
        for el in html.iter():
            if el.tag == tag1 or el.tag == tag2:
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
        lsts = self.find_all_two('ol', 'ul', self.html)
        for lst in lsts:
            lst.getchildren()[0].is_first_list_item = True
            lst.getchildren()[-1].is_last_list_item = True
        for el in self.html.find_first('body').iter():
            if el.tag == 'li':
                if self.check_for_lst_parent(el.parent) is False and el.is_first_list_item is True:
                    numId+= 1
                    ilvl=0
                if el.is_first_list_item is True:
                    ilvl+= 1
                el.ilvl=ilvl
                el.num_id = numId



    def parse(self, el):
        for child in el.getchildren():
                parsed = ''
                self.parse(child)
                if child.tag == 'li':
                    parsed = document_builder.DocxBuilder.li(child.text, child.ilvl, child.num_id, bold = False)
                    print parsed
                if child.tag == 'p':
                    parsed = document_builder.DocxBuilder.p_tag(child.text, self.bold)
                elif child.tag == 'b':
                    self.bold = True
                elif child.tag == 'i':
                    pass
                elif child.tag == 'u':
                    pass
