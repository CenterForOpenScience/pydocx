from pydocx.DocxParser import DocxParser


class Docx2LaTex(DocxParser):

    def __init__(self, *args, **kwargs):
        self.table_info = []
        super(Docx2LaTex, self).__init__(*args, **kwargs)

    @property
    def parsed(self):
        content = r"%(head)s\begin{document}%(content)s\end{document}" % {
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
        return '\n\n'

    def bold(self, text):
        return r'\textbf{%s}' % text

    def italics(self, text):
        return r'\emph{%s}' % text

    def underline(self, text):
        return r'\underline{%s}' % text

    def list_element(self, text):
        return r'\item %s' % text + '\n'

    def ordered_list(self, text, list_style):
        return r'\begin{enumerate} %s \end{enumerate}' % text

    def unordered_list(self, text):
        return r'\begin{itemize} %s \end{itemize}' % text

    def head(self):
        return r'''\documentclass{article}\usepackage{hyperref}
               \usepackage{graphicx}\usepackage{changes}
               \usepackage{changepage}
               \usepackage[paperwidth=%spt]{geometry}
               \usepackage{hanging}\usepackage{multirow}
               \usepackage{pbox}''' % self.page_width

    def paragraph(self, text, pre=None):
        return text + '\n\n'

    def heading(self, text, heading_value):
        #TODO figure out what to do for headings
        return text

    def insertion(self, text, author, date):
        return r'\added[id='+author+',remark='+date+']{%s}' % text

    def hyperlink(self, text, href):
        if text == '':
            return ''
        return r'\href{%(href)s}{%(text)s}' % {
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
            return r'\includegraphics[height=%spt, width=%spt]{%s}' % (
                y,
                x,
                src)
        else:
            return r'\includegraphics {%s}' % src

    def tab(self):
        return '\\qquad '

    def table(self, text):
        center = False
        right = False
        setup_cols = ''
        for i in range(self.cols + 1):
            for column in self.table_info:
                if column['Column'] == i   and column['justify'] == 'center':
                    center = True
                elif column['Column'] == i  and column['justify'] == 'right':
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
        return '\n' + r'\begin{tabular}{%s}' % setup_cols\
               + '\n' + r'%s\end{tabular}'\
               % text + '\n'

    def table_row(self, text):
        return text

    def table_cell(self, text, col='', row=''):
        slug = ''
        if col:
            slug += r'\multicolumn{%s}{l}' % col
        if row:
            slug += r'\multirow{%s}{*}' % row
        if self.line_break_in_table:
            slug += '{' + text + '}'
#            slug += r'\pbox{20cm}{' + text + '}'
        else:
            slug += text
        if self.last_row_item:
            slug += r' \\' + '\n'
            return slug
        self.line_break_in_table = False
        return '%s & ' % text

    def page_break(self):
        return r'\newpage '

    def indent(self, text, just='', firstLine='',
               left='', right='', hanging=''):
        if not self.indent_table:
            raggedright = False
            raggedleft = False
            center = False
            slug = ''
            if hanging:
                return r'\begin{hangparas}{%spt}{1} %s ' \
                       r'\end{hangparas}' % (hanging, text) + '\n'
            if right and left:
                left = float(left)
                right = float(right)
                left = left * float(3) / float(4)
                right = right * float(3) / float(4)
                slug += r'\begin{adjustwidth}{%spt}{%spt}' % (left, right)
            elif left:
                left = float(left)
                left = left * float(3) / float(4)
                slug += r'\begin{adjustwidth}{}{%spt}' % (left)
            elif right:
                right = float(right)
                right = right * float(3) / float(4)
                slug += r'\begin{adjustwidth}{%spt}{}' % (right)
            if firstLine:
                slug += r'\setlength{\parindent}{'+firstLine+r'pt}\indent '
            if just:
                if just == 'left':
                    raggedright = True
                    slug += r'\begin{flushright} '
                elif just == 'center':
                    center = True
                    slug += r'\begin{center} '
                elif just == 'right':
                    raggedleft = True
                    slug += r'\begin{flushleft} '
            slug += text
            if left or right:
                slug += r'\end{adjustwidth}'
            if raggedright:
                slug += r'\end{flushright}'
            if center:
                slug += r'\end{center}'
            if raggedleft:
                slug += r'\end{flushleft}'
            return slug
        else:
            self.columns = {}
            self.columns['Column'] = self.column_index
            self.columns['justify'] = just
            if self.columns not in self.table_info:
                self.table_info.append(self.columns)
            return text

    def break_tag(self):
        if self.is_table:
            self.line_break_in_table = True
        return ''

    def deletion(self, text, author, date):
        return r'\deleted[id='+author+',remark='+date+']{%s}' % text
