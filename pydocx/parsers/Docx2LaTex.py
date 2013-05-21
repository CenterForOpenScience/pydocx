from pydocx.DocxParser import DocxParser


class Docx2LaTex(DocxParser):

    def __init__(self, *args, **kwargs):
        self.rows = 0
        self.cols = 0
        self.current_col = 0
        self.table_info = []
        self.columns = {}
        super(Docx2LaTex, self).__init__(*args, **kwargs)

    @property
    def parsed(self):
        content = "%(head)s\\begin{document}%(content)s\\end{document}" % {
            'head': self.head(),
            'content': self._parsed}
        return unicode(content)

    def escape(self, text):
        chars = ['%', '&', '#', '$', '~', '_', '^', '{', '}']
        for ch in chars:
            if ch in text:
                text = text.replace(ch, '\\'+ch)
        return text

    def linebreak(self):
        return '\\\\ '

    def bold(self, text):
        return '\\textbf {%s}' % text

    def italics(self, text):
        return '\\emph {%s}' % text

    def underline(self, text):
        return '\\underline {%s}' % text

    def list_element(self, text):
        return '\\item {%s}' % text

    def ordered_list(self, text, list_style):
        return '\\begin{itemize}{%s}\\end{{enumerate}}' % text

    def unordered_list(self, text):
        return '\\begin{itemize}{%s}\\end{{itemize}}' % text

    def head(self):
        return "\\documentclass{article}\\usepackage{hyperref}"\
               "\\usepackage{graphicx}\\usepackage{changes}" \
               "\\usepackage{changepage} "\
               "\\usepackage[paperwidth=%spt]{geometry}" \
               "\\usepackage{hanging}" % self.page_width

    def paragraph(self, text, pre=None):
        return '\\par{'+text+'} '

    def heading(self, text, heading_value):
        #TODO figure out what to do for headings
        return text

    def insertion(self, text, author, date):
        return '\\added[id='+author+',remark='+date+']{%s}' % text

    def hyperlink(self, text, href):
        if text == '':
            return ''
        return '\\href{%(href)s}{%(text)s}' % {
            'href': href,
            'text': text,
        }

    def image_handler(self, path):
        return path

    def image(self, path, x, y):
        src = self.image_handler(path)
        if not src:
            return ''
        if all([x, y]):
            x = x.replace('px', '')
            y = y.replace('px', '')
            x = float(x)
            y = float(y)
            x = x * float(3) / float(4)
            y = y * float(3) / float(4)
            return '\\includegraphics[height=%spt, width=%spt] {%s}' % (
                y,
                x,
                src)
        else:
            return '\\includegraphics {%s}' % src

    def tab(self):
        return '\\qquad '

    def table(self, text):
        center = False
        right = False
        setup_cols = ''
        print self.cols
        for i in range(self.cols):
            for column in self.table_info:
                if column['Column'] == i and column['justify'] == 'center':
                    center = True
                elif column['Column'] == i and column['justify'] == 'right':
                    right = True
            if center is True:
                setup_cols += 'c'
                center = False
            elif right is True:
                setup_cols += 'r'
                right = False
            else:
                setup_cols += 'l'
        self.table_info = []
        return '\\\\\\begin{tabular} {%s} %s \\end{tabular}\\\\ ' \
               % (setup_cols, text)

    def table_row(self, text):
        return '%s \\\\ ' % text

    def table_cell(self, text, last, col_index, row_index, col='', row=''):
        if last is True:
            self.cols = col_index + 1
            self.rows = row_index + 1
            return text
        else:
            return '%s & ' % text

    def page_break(self):
        return '\\newpage '

    def indent_table(self, just='', firstLine='', left='', right='', column=0):
        self.columns = {}
        self.columns['Column'] = column
        self.columns['justify'] = just
        if self.columns not in self.table_info:
            self.table_info.append(self.columns)
        return ''

    def indent(self, text, just='', firstLine='',
               left='', right='', hanging=0):
        raggedright = False
        raggedleft = False
        center = False
        slug = '{'
        if hanging:
            slug += '\\begin{hangpara}{%spt}{1} ' % (hanging)
        if left and not right:
            left = float(left)
            left = left * float(3) / float(4)
            slug += '\\begin{adjustwidth}{}{%spt}' % (left)
        if right and not left:
            right = float(right)
            right = right * float(3) / float(4)
            slug += '\\begin{adjustwidth}{%spt}{}' % (right)
        if right and left:
            left = float(left)
            right = float(right)
            left = left * float(3) / float(4)
            right = right * float(3) / float(4)
            slug += '\\begin{adjustwidth}{%spt}{%spt}' % (left, right)
        if firstLine:
            slug += '\\setlength{\\parindent}{'+firstLine+'pt}\\indent '
        if just:
            if just == 'left':
                raggedright = True
                slug += '\\begin{flushright} '
            elif just == 'center':
                center = True
                slug += '\\begin{center} '
            elif just == 'right':
                raggedleft = True
                slug += '\\begin{flushleft} '
        slug += text
        if left or right:
            slug += '\\end{adjustwidth}'
        if hanging:
            slug += '\\end{hangpara}'
        if raggedright:
            slug += '\\end{flushright}'
        if center:
            slug += '\\end{center}'
        if raggedleft:
            slug += '\\end{flushleft}'
        slug += '}'
        return slug
        #TODO left and right

    def break_tag(self):
        return ''

    def deletion(self, text, author, date):
        return '\\deleted[id='+author+',remark='+date+']{%s}' % text
