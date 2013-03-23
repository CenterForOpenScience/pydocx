import zipfile
from lxml import etree
from StringIO import StringIO
__author__ = 'samportnow'

#for el in tree.iter():
    # The way lists are handled could double visit certain elements; keep
    # track of which elements have been visited and skip any that have been
    # visited already.
    #if el in visited_nodes:
        #continue
#with zipfile.ZipFile('/Users/samportnow/Documents/pydocx/helloworld.docx') as f:
#    document = f.read('word/document.xml')
#    numbering= f.read('word/numbering.xml')
#parser=etree.XMLParser(ns_clean=True)
#document=StringIO(document)
#numbering=StringIO(numbering)
#numbering_tree=etree.parse(numbering,parser)
#numbering_namespace=numbering_tree.getroot().nsmap['w']
#visited_els=[]

def get_parsed():
    parser=etree.XMLParser(ns_clean=True)
    tree=etree.parse(document,parser)
    namespace=tree.getroot().nsmap['w']
    #rpr is run properties for the paragraph mark
    paragraph=''
    run_text=''
    running_text=''
    for el in tree.iter():
        if el.tag=='{%s}p' %namespace:
            for wp in el.iter():
                if wp.tag =='{%s}ins' %namespace:
                    for text in wp.iterchildren():
                        if text not in visited_els:
                            run_text +='<div class=insert>'+get_text(text,namespace,visited_els)+'</div>'
                            visited_els.append(text)
                if wp.tag=='{%s}r' %namespace and wp not in visited_els:
                    run_text+=get_text(wp,namespace,visited_els)
                    visited_els.append(wp)
                if not el.getchildren():
                    run_text+='<br>'
                if wp.tag == '{%s}ilvl' %namespace:
                    for lst in el.iter():
                        if lst.find('{%s}numId' %namespace) is not None and el not in visited_els:
                            numval = lst.find('{%s}numId' %namespace).attrib['{%s}val' %namespace]
                            lst_type=get_list_style(numval)
                        if get_text(lst,namespace,visited_els) and el not in visited_els and lst_type['{%s}val' %namespace] != 'bullet':
                            if lst.getnext() is not None:
                                if lst not in visited_els:
                                    while lst.getnext() is not None:
                                        if lst not in visited_els:
                                            text = get_text(lst,namespace,visited_els)
                                            next_txt = get_text(lst.getnext(),namespace,visited_els)
                                            running_text += text + next_txt
                                            visited_els.append(lst)
                                            visited_els.append(lst.getnext())
                                            lst=lst.getnext()
                                        else:
                                            run_text += '<li>' + running_text + '</li>'
                                            break
                            else:
                                run_text +='<li>' +  get_text(lst, namespace, visited_els) + '</li>'
                                visited_els.append(lst)
    print running_text
    return run_text


def get_text(wp,namespace,visited_els):
    run_text= ''
    decorator = ''
    closing = ''
    if wp.find('{%s}tab' %namespace) is not None:
        run_text+='%nbsp'
    if wp.find('{%s}rPr' %namespace) is not None:
        for tag in wp.iter():
            if tag.find('{%s}u' %namespace) is not None:
                if wp.find('{%s}t' %namespace) is not None:
                    decorator +='<u>'
                    closing += '</u>'
                    visited_els.append(wp.find('{%s}t' %namespace))
            if tag.find('{%s}i' %namespace) is not None:
                if wp.find('{%s}t' %namespace) is not None:
                    decorator += '<i>'
                    closing += '</i>'
                    visited_els.append(wp.find('{%s}t' %namespace))
            if tag.find('{%s}b' %namespace) is not None:
                if wp.find('{%s}t' %namespace) is not None:
                    decorator += '<b>'
                    closing += '</b>'
                    visited_els.append(wp.find('{%s}t' %namespace))
        run_text = wp.find('{%s}t' %namespace).text
        run_text = decorator + run_text + closing
    if wp.find('{%s}t' %namespace) is not None and wp.find('{%s}t' %namespace) not in visited_els:
        run_text+=wp.find('{%s}t' %namespace).text
    return run_text

def get_list_style(numval):
    ids = numbering_tree.findall('{%s}num' %numbering_namespace)
    for id in ids:
        if id.attrib['{%s}numId' %numbering_namespace] == numval:
            abstractid=id.find('{%s}abstractNumId' %numbering_namespace)
            abstractid=abstractid.attrib['{%s}val' %numbering_namespace]
            style_information=numbering_tree.findall('{%s}abstractNum' %numbering_namespace)
            for info in style_information:
                if info.attrib['{%s}abstractNumId' %numbering_namespace] == abstractid:
                    for i in info.iter():
                        if i.find('{%s}numFmt' %numbering_namespace) is not None:
                            return i.find('{%s}numFmt' %numbering_namespace).attrib

#print get_parsed()
