from pydocx import docx2html, Docx2Html, docx2latex
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ElementTree
import benchmark

class Benchmark_Sqrt(benchmark.Benchmark):

    each = 10

    def test_docx(self):
        with open('test.html', 'w') as f:
            f.write(docx2html('/Users/samportnow/Documents/bigger_doc.docx').encode('utf-8'))

if __name__ == '__main__':
    benchmark.main(format="markdown", numberFormat="%.4g")

#with open('test.tex', 'w') as f:
#    f.write(docx2latex('/Users/samportnow/Documents/Nosek Articles/HN2012.docx').encode('utf-8'))
#
#
#with open('test.html', 'w') as f:
#    f.write(docx2html('/Users/samportnow/Documents/Nosek Articles/HN2012.docx').encode('utf-8'))
##with open('test.html', 'w') as f:
##    f.write(docx2html('/Users/samportnow/Documents/Nosek Articles/Letal2013.docx').encode('utf-8'))
##print docx2html('/Users/samportnow/Documents/policy.docx')
##
#print BeautifulSoup(
#    ElementTree.tostring(
#        Docx2Html('/Users/samportnow/Documents/landscape.docx').root,
#    ),
#).prettify()