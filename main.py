from pydocx import docx2html, docx2latex

print docx2html('./pydocx/fixtures/simple_table.docx')


with open('test.tex', 'w') as f:
 f.write(docx2latex('/Users/samportnow/Documents/motor-dediff-prod.docx'))

#print test_table.get_xml()

#print test_xml.TableTag(_TranslationTestCase).get_xml()

#for (dirpath, dirnames, filenames)
# in os.walk('/Users/samportnow/Documents/pydocx/pydocx/fixtures'):
#    for fi in filenames:
#        try:
#            print 'THE TEST IS ' + fi
#            print docx2markdown
# ('/Users/samportnow/Documents/pydocx/pydocx/fixtures/'+fi)
#        except:
#            print 'had to pass it'
