from pydocx import *

with open('test.html', 'w') as f:
    f.write(docx2html('helloworld.docx'))
print docx2html('helloworld.docx')
#print docx2markdown('helloworld.docx')