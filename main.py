from pydocx import docx2html, Docx2Html, docx2markdown, Docx2Markdown, docx2xml, Docx2LaTex,\
    docx2latex
from pydocx.tests import test_xml
from pydocx.tests import document_builder
from pydocx.tests import XMLDocx2Html
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ElementTree

#print BeautifulSoup(
#    ElementTree.tostring(
#        Docx2Html('./pydocx/fixtures/simple_table.docx').root,
#    ),
#).prettify()
print docx2html('./pydocx/fixtures/simple_table.docx')


#print test_table.get_xml()

#print test_xml.TableTag(_TranslationTestCase).get_xml()

#for (dirpath, dirnames, filenames) in os.walk('/Users/samportnow/Documents/pydocx/pydocx/fixtures'):
#    for fi in filenames:
#        try:
#            print 'THE TEST IS ' + fi
#            print docx2markdown('/Users/samportnow/Documents/pydocx/pydocx/fixtures/'+fi)
#        except:
#            print 'had to pass it'