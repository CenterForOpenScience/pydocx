from pydocx import docx2html, Docx2Html
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree


with open('test.html', 'w') as f:
    f.write(docx2html('./helloworld.docx'))
with open('testxml.html', 'w') as f:
    f.write(
        BeautifulSoup(
            ElementTree.tostring(
                Docx2Html('./helloworld.docx').root,
            ),
        ).prettify(),
    )
print docx2html('./helloworld.docx')
print BeautifulSoup(
    ElementTree.tostring(
        Docx2Html('./helloworld.docx').root,
    ),
).prettify()
