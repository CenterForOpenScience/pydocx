from pydocx import *
from bs4 import BeautifulSoup

with open('test.html', 'w') as f:
    f.write(docx2html('helloworld.docx'))
#with open('testxml.html','w') as f:
#    f.write(Docx2Html('helloworld.docx').document.prettify())

#print docx2html('helloworld.docx')
#print docx2markdown('helloworld.docx')