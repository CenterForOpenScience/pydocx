__author__ = 'samportnow'
from bs4 import BeautifulSoup
import zipfile
from pydocx.DocxParser import ElementTree
from pydocx.py_docx.docx import *
import py_docx.docx as docx
import os

class Html2Docx():

    def __init__(self, html):
        # set up what is parsed
        self.parsed = ''
        with open(html, 'r') as f:
            html = f.read()
        # set up the html
        self.html = ElementTree.fromstring(html)
        # get the relationship list
        self.relationships = relationshiplist()
        # make a new document
        self.document = newdocument()
        #make the document
        self.body = self.document.xpath('/w:document/w:body', namespaces=nsprefixes)[0]
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
        ilvl = -1
        numId = 0
        lsts = self.find_all_by_tags(self.html, 'ol', 'ul')
        for lst in lsts:
            lst.getchildren()[0].is_first_list_item = True
            lst.getchildren()[-1].is_last_list_item = True
        for el in self.html.find('body').iter():
            if el.tag == 'li':
                if self.check_for_lst_parent(el.parent) \
                   is False and el.is_first_list_item is True:
                    numId += 1
                    ilvl = -1
                if el.is_first_list_item is True:
                    ilvl += 1
                el.ilvl = ilvl
                el.num_id = numId
                el.is_list_item = True

    def justificaton(self, el):
        pass

    def parse(self, el):
        for child in el.getchildren():
            if child.tag == 'p':
                text_and_style = self.parse_r(child)
                self.body.append(paragraph(text_and_style))
            if child.tag == 'ul' or child.tag == 'ol':
                lst_type = child.tag
                self.parse_list(child, lst_type)
            if child.tag == 'table':
                self.body.append(self.parse_table(child))
            self.parse(child)
        self.save()

    def parse_r(self, el):
        par_block = []
        breaks = []
        style = ''
        for child in el.iter():
            text = ''
            if child.tag == 'em':
                style += 'i'
            if child.tag == 'strong':
                style += 'b'
            if child.tag == 'underline':
                style += 'u'
            if child.text:
                text = child.text
            if child.tag == 'br':
                text = child.tail
                breaks.append('br')
            if text:
                par_block.append([text, style, breaks])
                style = ''
            if child.parent.tag == 'li':
                return par_block
        return par_block


    def parse_list(self, lst, lst_type = ''):
        for child in lst.getchildren():
            if child.tag == 'li':
                text_and_style = self.parse_r(child)
            self.body.append(
                paragraph(
                    text_and_style, is_list=True, ilvl=str(child.ilvl), numId=str(child.num_id), style=lst_type))

    def table_look_ahead(self, tbl):
        columns = 0
        trs = tbl.find_all('tr')
        tcs = trs[0].find_all('td')
        for tc in tcs:
            if 'colspan' in tc.attrib:
                columns += int(tc.attrib['colspan'])
            else:
                columns += 1
        return columns

    def parse_table(self, el):
        columns = self.table_look_ahead(el)
        tbl = createtblproperties(columns)
        for tr in el.getchildren():
            table_row = createtablerow()
            tcs = tr.find_all('td')
            for tc in tcs:
                if "colspan" in tc.attrib:
                    cell = createtablecell(gridspan=tc.attrib["colspan"])
                if "rowspan" in tc.attrib:
                    print "ya buddy"
                    print tc.attrib["rowspan"]
                else:
                    cell = createtablecell()
                if tc.text:
                    text_and_style = self.parse_r(tc)
                    par_run=paragraph(text_and_style)
                    cell.append(par_run)
                table_row.append(cell)
            tbl.append(table_row)
        return tbl


    def save(self):
        title = 'Python docx demo'
        subject = 'A practical example of making docx from Python'
        creator = 'Mike MacCana'
        keywords = ['python', 'Office Open XML', 'Word']
#        print BeautifulSoup(
#        ElementTree.tostring(
#        self.document,
#        ),
#        ).prettify()
        coreprops = coreproperties(title=title, subject=subject, creator=creator,
            keywords=keywords)
        appprops = appproperties()
        contenttypes = docx.contenttypes()
        websettings = docx.websettings()
        wordrelationships = docx.wordrelationships(self.relationships)
        # Save our document
        savedocx(self.document, coreprops, appprops, contenttypes, websettings,
            wordrelationships, 'Testing.docx')
