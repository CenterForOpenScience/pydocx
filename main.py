from pydocx import docx2html, Docx2Html
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree


with open('test.html', 'w') as f:
    f.write(docx2html('./pydocx/fixtures/nested_tables.docx'))
with open('testxml.html', 'w') as f:
    f.write(
        BeautifulSoup(
            ElementTree.tostring(
                Docx2Html('./pydocx/fixtures/nested_tables.docx').root,
            ),
        ).prettify(),
    )
print docx2html('./pydocx/fixtures/nested_tables.docx')
print BeautifulSoup(
    ElementTree.tostring(
        Docx2Html('./pydocx/fixtures/nested_tables.docx').root,
    ),
).prettify()
