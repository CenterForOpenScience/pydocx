import sys

from pydocx.DocxParser import DocxParser


class Docx2Markdown(DocxParser):
    def escape(self, text):
        return text

    def linebreak(self):
        return '\n'

    def paragraph(self, text):
        return text + '\n'

    def insertion(self, text, author, date):
        pass

    def bold(self, text):
        return '**' + text + '**'

    def italics(self, text):
        # TODO do we need a "pre" variable, so I can check for
        # *italics**italics* and turn it into *italicsitatlics*?
        return '*' + text + '*'

    def underline(self, text):
        return '***' + text + '***'


def main():
    try:
        path_to_docx = sys.argv[1]
        path_to_html = sys.argv[2]
    except IndexError:
        print 'Must specific the file to convert and the name of the resulting file.'  # noqa
        sys.exit()
    html = Docx2Markdown(path_to_docx).parsed
    with open(path_to_html, 'w') as f:
        f.write(html)

if __name__ == '__main__':
    main()
