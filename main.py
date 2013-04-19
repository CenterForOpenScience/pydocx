from pydocx import *
#from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree
#import lxml.etree as etree

with open('test.html', 'w') as f:
    f.write(docx2html('helloworld.docx'))
#with open('testxml.html','w') as f:
#    f.write(BeautifulSoup(ElementTree.tostring(Docx2Html('helloworld.docx').root)).prettify())

#print docx2html('helloworld.docx')
#print docx2markdown('helloworld.docx')
