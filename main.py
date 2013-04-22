from pydocx import *
from BeautifulSoup import BeautifulSoup
import xml.etree.ElementTree as ElementTree


with open('test.html', 'w') as f:
    f.write(docx2html('helloworld.docx'))
with open('testxml.html','w') as f:
    f.write(BeautifulSoup(ElementTree.tostring(Docx2Html('helloworld.docx').root)).prettify())

