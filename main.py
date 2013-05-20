from pydocx import docx2html, Docx2Html, docx2latex
from bs4 import BeautifulSoup
from pydocx.tests import document_builder
import xml.etree.ElementTree as ElementTree


print docx2latex('./helloworld.docx')
#print docx2html('./pydocx/fixtures/simple.docx')
#print BeautifulSoup(
#    ElementTree.tostring(
#        Docx2Html('./pydocx/fixtures/simple.docx').root,
#    ),
#).prettify()

