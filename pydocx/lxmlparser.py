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
def get_parsed():
    with zipfile.ZipFile('/Users/samportnow/Documents/pydocx/helloworld.docx') as f:
        document = f.read('word/document.xml')
        numbering= f.read('word/numbering.xml')
    parser=etree.XMLParser(ns_clean=True)
    tree=etree.parse('/Users/samportnow/Documents/pydocx/helloworld/word/document.xml',parser)
    namespace=tree.getroot().nsmap['w']
    #rpr is run properties for the paragraph mark
    paragraph=''
    run_text=''
    visited_els=[]
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
                    for wp in el.iter():
                        if wp not in visited_els and get_text(wp,namespace,visited_els) :
                            run_text+='<li>' + get_text(wp,namespace,visited_els) + '</li>'
                            visited_els.append(wp)
    return run_text


def get_text(wp,namespace,visited_els):
    run_text=''
    if wp.find('{%s}tab' %namespace) is not None:
        run_text+='%nbsp'
    if wp.find('{%s}rPr' %namespace) is not None:
        for tag in wp.iter():
            if tag.find('{%s}u' %namespace) is not None:
                if wp.find('{%s}t' %namespace) is not None:
                    run_text+='<u>' + wp.find('{%s}t' %namespace).text +'</u>'
                    visited_els.append(wp.find('{%s}t' %namespace))
                    break
    if wp.find('{%s}rPr' %namespace) is not None:
        for tag in wp.iter():
            if tag.find('{%s}i' %namespace) is not None:
                if wp.find('{%s}t' %namespace) is not None:
                    run_text+='<i>' + wp.find('{%s}t' %namespace).text +'</i>'
                    visited_els.append(wp.find('{%s}t' %namespace))
                    break
    if wp.find('{%s}rPr' %namespace) is not None:
        for tag in wp.iter():
            if tag.find('{%s}b' %namespace) is not None:
                if wp.find('{%s}t' %namespace) is not None:
                    run_text+='<b>' + wp.find('{%s}t' %namespace).text +'</b>'
                    visited_els.append(wp.find('{%s}t' %namespace))
                    break
    if wp.find('{%s}t' %namespace) is not None and wp.find('{%s}t' %namespace) not in visited_els:
        run_text+=wp.find('{%s}t' %namespace).text
    return run_text

print get_parsed()
