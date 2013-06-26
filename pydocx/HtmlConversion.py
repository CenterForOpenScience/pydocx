import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import _ElementInterface
from pydocx.py_docx.docx import *
import py_docx.docx as docx


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


def has_descendant_with_tag(el, tag):
    """
    Determine if there is a child ahead in the element tree.
    """
    # Get child. stop at first child.
    return True if el.find('.//' + tag) is not None else False


setattr(_ElementInterface, 'find_first', find_first)
setattr(_ElementInterface, 'find_all', find_all)
setattr(_ElementInterface, 'is_first_list_item', False)
setattr(_ElementInterface, 'is_last_list_item', False)
setattr(_ElementInterface, 'in_table', False)
setattr(_ElementInterface, 'has_descendant_with_tag', has_descendant_with_tag)
setattr(_ElementInterface, 'new_list', False)
setattr(_ElementInterface, 'new_ilvl', False)
setattr(_ElementInterface, 'is_first_list', False)
setattr(_ElementInterface, 'is_last_item_in_list', False)


class Html2Docx():

    def __init__(self, html):
        # set up what is parsed
        self.parsed = ''
        with open(html, 'r') as f:
            html = f.read()
        # need to keep track of elements
        # that have been visited
        self.visited = []
        self.stored_numId = 0
        # need to keep track of the
        # ilvl in the document
        self.stored_ilvl = 0
        #abstractId info for the numbering documents
        self.abstractIdInfo = []
        #numIds for the numbering document.
        #these correspond to the abstractIdInfo
        self.numIds = []
        #for the numbering document
        self.abstract = None
        # set up the html
        self.html = ElementTree.fromstring(html)
        # get the relationship list
        self.relationships = relationshiplist()
        # make a new document
        self.document = newdocument()
        #get the body
        self.body = self.document.xpath(
            '/w:document/w:body', namespaces=nsprefixes)[0]
        #make a new numbering document
        self.numbering = new_numbering()
        #start bulding the document
        self.build()

    def build(self):
        #first step is to add parent attribute
        #for the whole document
        def add_parent(el):
            for child in el.getchildren():
                setattr(child, 'parent', el)
                add_parent(child)
        add_parent(self.html)
        #now set the list attributes
        self.set_list_attributes()
        #and begin parsing
        self.parse(self.html.find_first('body'))

    def find_all_by_tags(self, html, *args):
        #helper function to find all the elements
        #with mutiple tags
        list_elements = []
        for el in html.iter():
            if el.tag in args:
                list_elements.append(el)
        return list_elements

    def check_for_lst_parent(self, el):
        #helper function to see if a list
        #has an li as a parent.
        #meaning that its parent is itself
        #a list and therefore, it is nested
        lst_parent = False
        if el.parent.tag != 'body':
            if el.parent.tag == 'li':
                lst_parent = True
                #return true if you find a list parent
                return lst_parent
            self.check_for_lst_parent(el.parent)
        else:
            return lst_parent

    def set_list_attributes(self):
        #now we set the list attributes
        ilvl = 0
        numId = 0
        lsts = self.find_all_by_tags(self.html, 'ol', 'ul')
        for lst in lsts:
            lst.getchildren()[0].is_first_list_item = True
            lst.getchildren()[-1].is_last_list_item = True
            for item in lst.getchildren():
                #if the element does not have a parent and it is
                #the last list item, we know it is safe to
                #increment the numId, meaning there is a new
                #list
                if not self.check_for_lst_parent(item.parent):
                    if item.is_last_list_item:
                        numId += 1
                        #has to be true because a new list will
                        # automatically have a new ilvl
                        item.new_ilvl = True
                        item.new_list = True
                        #also have to set the ilvl back to 0
                        ilvl = 0
                elif item.is_first_list_item and self.check_for_lst_parent(
                        item.parent):
                    #if a list if item has a parent that is a list
                    #and its the first item, we must increment the
                    #indentation level (ilvl)
                    item.new_ilvl = True
                    ilvl += 1
                item.ilvl = ilvl
                item.num_id = numId
                item.is_list_item = True

    def parse(self, el):
        for child in el.getchildren():
            if child.tag == 'br':
                #if we find a break tag, look for text after it
                text_and_style = self.parse_r(child)[0]
                just = self.parse_r(child)[1]
                self.body.append(paragraph(text_and_style, jc=just))
            if child.tag == 'p':
                #if we find a p tag, look for text after it
                text_and_style = self.parse_r(child)[0]
                just = self.parse_r(child)[1]
                self.body.append(paragraph(text_and_style, jc=just))
            if child.tag == 'ul' or child.tag == 'ol':
                #if we find a list, look for text after it
                lst_type = child.tag
                self.parse_list(child, lst_type)
            if child.tag == 'table':
                #separate function for parsing tables
                #because in word, the table tags are the parent
                #of the p tag, so we have to handle
                #them a bit differently
                self.body.append(self.parse_table(child))
            self.parse(child)
        self.save()

    def parse_r(self, el):
        # we have to the whole block of
        # text that will go in a paragraph
        par_block = []
        # we have to get the breaks that
        # will go in the paragraph
        breaks = []
        #we need this to creating a string of the styles
        #i.e., bold, italic, underline
        style = ''
        just = 'left'
        for child in el.iter():
            text = ''
            if child.tag == 'div':
                #look for what the justification is
                if 'center' in child.attrib['class']:
                    just = 'center'
                elif 'right' in child.attrib['class']:
                    just = 'right'
            if child.tag == 'em':
                #if there's an em tag,
                #add italic to style
                style += 'i'
            if child.tag == 'strong':
                #if there's a strong tag,
                #add bold to style
                style += 'b'
            if child.tag == 'underline':
                #if there's an underline tag,
                #add underline to style
                style += 'u'
            if child.text:
                #get the text
                text = child.text
            if child.tag == 'br' and child not in self.visited:
                #dont want to hit breaks twice
                #text of break comes at the tail
                text = child.tail
                breaks.append('br')
                self.visited.append(child)
            if text:
                #if text, add everything to the parblock
                #set the style back to blank
                par_block.append([text, style, breaks])
                style = ''
            if child.parent and child.parent.tag == 'li':
                #if it has a list parent, return early
                return par_block, just
        return par_block, just

    def parse_list(self, lst, lst_type=''):
        tentatives = None
        """
        parsing lists, we need to keep track of both
        the list itself, and as we go through build up
        the numbering document. for some reason,
        there are two sections of a word numbering document:
        an abstract numbering section that contains all of the
        relevant list info, as well as a num section that contains
        references to the abstract numbers defined earlier in the
        numbering file
        """
        for child in lst.getchildren():
            if child not in self.visited:
                #first append the elements to
                #the visisted elements
                self.visited.append(child)
                #get the text and style of this child
                text_and_style = self.parse_r(child)[0]
                #get the justication of the style
                just = self.parse_r(child)[1]
                #if its an ol, then its a decimal list
                if lst_type == 'ol':
                    type_lst = 'decimal'
                #if its a ul, then its a bulleted list
                if lst_type == 'ul':
                    type_lst = 'bullet'
                if child.new_ilvl:
                    #if theres a new ilvl, increase
                    #the indentation
                    ind = 720 * (child.ilvl + 1)
                    #create a numId attribute for the list, this
                    #is for the numbering document,
                    num = create_list_attributes(
                        ilvl=str(child.ilvl),
                        type=type_lst, just=just, left=str(ind))
                    #append that numId to the lists of
                    #all the numIds
                    #we will later append this info to the
                    #abstract id section of the numbering document
                    self.numIds.append(num)
                    self.stored_ilvl += 1
                if not child.find('ol') and not child.find('ul'):
                    tentatives = fill_tentative(
                        self.stored_ilvl, type_lst=type_lst)
                    #if we cant find another list, we know its the
                    #last item and it's ok to fill out the rest of the
                    #abstract num info

                    #abstractnumid gets increased
                    # for every list, starts out at 0. numIds themselves
                    self.abstract = create_list(child.num_id - 1)
                    self.numbering.append(self.abstract)
                    #here is where we append to the abstract num section
                    for num in self.numIds:
                        self.abstract.append(num)
                    #now we have to create tentative lists. the way that
                    #word is able to nicely do indent to create new lists
                    #is by creating tentative lists that start past the
                    #last indent. it goes all the way up to 8, because that's
                    #all that will fit in the width of the file.
                    for tentative in tentatives:
                        self.abstract.append(tentative)
                    #now we have our abstract id info, and we have to append to
                    #it the current num_id
                    self.abstractIdInfo.append(
                        create_abstract_IdInfo(str(child.num_id)))
                    #we're done here, so we can set our stored_ilvl back to 0
                    self.stored_ilvl = 0
                    #and we can set our num ideas to zero
                    self.numIds = []
                #now we append to hte body the relavent list info
                self.body.append(
                    paragraph(
                        text_and_style, is_list=True,
                        ilvl=str(child.ilvl), numId=str(child.num_id),
                        style=lst_type, jc=just))
            #if, from the current list element, we find another list,
            # we have to parse that lists BEFORE we parse the next list
            # item in the current list
            if child.find('ul'):
                lst = child.find('ul')
                self.parse_list(lst, lst.tag)
            if child.find('ol'):
                lst = child.find('ol')
                self.parse_list(lst, lst.tag)

    def table_look_ahead(self, tbl):
        #table look ahead function,
        #we need to do this to account for vertical merges. in html
        #all you need to do is include the rowspan and not include any
        #extra table elements. word, on the other hand, expects an
        #empty tale with a vmerge attribute inside it. so we're
        #going to go thru and create these elements and insert them
        #into the html document
        trs = tbl.find_all('tr')
        for i in range(len(trs)):
            tcs = trs[i].find_all('td')
            for j in range(len(tcs)):
                if 'rowspan' in tcs[j].attrib:
                    for x in range(1, int(tcs[j].attrib['rowspan'])):
                        tc = ElementTree.Element('td')
                        setattr(tc, 'parent', trs[i+x])
                        tc.set('vmerge_continue', True)
                        trs[i + x].insert(j, tc)
        return tbl

    def get_columns(self, tbl):
        #have to get the total number of columns
        #for the table. just go by the first row
        #but if there is a colspan, add that to the
        #column count
        columns = 0
        trs = tbl.find_all('tr')
        tcs = trs[0].find_all('td')
        for tc in tcs:
            tc.in_table = True
            if 'colspan' in tc.attrib:
                columns += int(tc.attrib['colspan'])
            else:
                columns += 1
        return columns

    def parse_table(self, el):
        #get the number of columns
        columns = self.get_columns(el)
        #set up the table properties
        tbl = createtblproperties(columns)
        #going to have to do a look ahead and
        #create those extra table rows
        for tr in self.table_look_ahead(el).getchildren():
            table_row = createtablerow()
            tcs = tr.find_all('td')
            for tc in tcs:
                colspan = ''
                vmerge = {}
                #now look for colspans
                #and rowspans (referenced by
                #total number of vmerge starting from
                #a vmerge:restart
                if 'colspan' in tc.attrib:
                    colspan = tc.attrib['colspan']
                if 'rowspan' in tc.attrib:
                    vmerge = {'val': 'restart'}
                if 'vmerge_continue' in tc.attrib:
                    vmerge = {'val': 'continue'}
                cell = createtablecell(gridspan=colspan, vmerge=vmerge)
                text_and_style = self.parse_r(tc)[0]
                just = self.parse_r(tc)[1]
                par_run = paragraph(text_and_style, jc=just)
                cell.append(par_run)
                table_row.append(cell)
            tbl.append(table_row)
        return tbl

    def save(self):
        title = 'Python docx demo'
        subject = 'A practical example of making docx from Python'
        creator = 'Mike MacCana'
        keywords = ['python', 'Office Open XML', 'Word']
        for abstract in self.abstractIdInfo:
            self.numbering.append(abstract)
        coreprops = coreproperties(
            title=title, subject=subject,
            creator=creator, keywords=keywords)
        appprops = appproperties()
        contenttypes = docx.contenttypes()
        websettings = docx.websettings()
        wordrelationships = docx.wordrelationships(self.relationships)
        # Save our document
        savedocx(
            self.document, coreprops,
            appprops, contenttypes, websettings,
            wordrelationships, 'Testing.docx', self.numbering)
