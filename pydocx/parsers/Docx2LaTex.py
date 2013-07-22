import base64
from pydocx.DocxParser import DocxParser


class Docx2LaTex(DocxParser):

    def __init__(self, *args, **kwargs):
        self.table_info = []
        self.counted_columns = False
        self.previous_orient = ''
        self.col_count = 0
        self.hit_list = False
        self.line_break_in_table = False
        super(Docx2LaTex, self).__init__(*args, **kwargs)

    @property
    def parsed(self):
        content = r"%(head)s\begin{document}%(content)s\end{document}" % {
            'head': self.head(),
            'content': self._parsed}
        return content.encode('utf-8')

    def escape(self, text):
        chars = ['%', '&', '#', '$', '~', '_', '^', '{', '}']
        for ch in chars:
            if ch in text:
                text = text.replace(ch, '\\'+ch)
        return text

    def linebreak(self):
        return '\n\n'

    def paragraph(self, text, pre=None):
        return text + '\n\n'

    def bold(self, text):
        return r'\textbf {%s}' % text

    def italics(self, text):
        return r'\emph {%s}' % text

    def underline(self, text):
        return r'\underline {%s}' % text

    def list_element(self, text):
        return r'\item %s' % text + '\n'

    def ordered_list(self, text, list_style):
        self.hit_list = True
        return r'\begin{enumerate} %s \end{enumerate}' % text

    def unordered_list(self, text):
        self.hit_list = True
        return r'\begin{itemize} %s \end{itemize}' % text

    def head(self):
        return r'''\documentclass{article}\usepackage{hyperref}
               \usepackage{graphicx}\usepackage{changes}
               \usepackage{changepage}
               \usepackage{hanging}\usepackage{multirow}
               \usepackage{pbox}\usepackage{pdflscape}
               \usepackage{ulem}\usepackage{comment}'''

    def heading(self, text, heading_value):
        if heading_value == 'h1':
            return r'\section{%s}' % text + '\n\n'
        elif heading_value == 'h2':
            return r'\subsection{%s}' % text + '\n\n'
        elif heading_value == 'h3':
            return r'\paragraph{%s}' % text + '\n\n'
        elif heading_value == 'h4':
            return r'\subparagraph{%s}' % text + '\n\n'
        else:
            return text + '\n\n'

    def insertion(self, text, author, date):
        return r'\added[id='+author+',remark='+date+']{%s}' % text

    def hyperlink(self, text, href):
        if text == '':
            return ''
        return r'\href{%(href)s}{%(text)s}' % {
            'href': href,
            'text': text,
        }

    def image_handler(self, image_data, filename):
        extension = filename.split('.')[-1].lower()
        b64_encoded_src = 'data:image/%s;base64,%s' % (
            extension,
            base64.b64encode(image_data),
        )
        b64_encoded_src = self.escape(b64_encoded_src)
        return b64_encoded_src

    def image(self, image_data, filename, x, y):
        src = self.image_handler(image_data, filename)
        if not src:
            return ''
        if all([x, y]):
            if x.find('px') != -1:
                x = x.replace('px', '')
                x = float(x)
                x = x * float(3) / float(4)
                x = str(x) + 'pt'
            elif y.find('px') != -1:
                y = y.replace('px', '')
                y = float(y)
                y = y * float(3) / float(4)
                y = str(y) + 'pt'
            return r'\includegraphics[height=%spt, width=%s]{%s}' % (
                y,
                x,
                src)
        else:
            return r'\includegraphics {%s}' % src

    def tab(self):
        return r'\qquad '

    def table(self, text):
        setup_cols = ''
        for i in range(0, self.col_count):
            match = next((
                column for column in self.table_info
                if 'Column' in column and column['Column'] == i), None)
            if match:
                if 'justify' in match:
                    if match['justify'] == 'center':
                        setup_cols += 'c'
                    elif match['justify'] == 'right':
                        setup_cols += 'r'
                elif match['list']:
                        setup_cols += 'p{3cm}'
            else:
                setup_cols += 'l'
        self.table_info = []
        return '\n' + r'\begin{tabular}{%s}' % setup_cols\
               + '\n' + r'%s\end{tabular}'\
               % text + '\n\n'

    def table_row(self, text):
        self.counted_columns = True
        return text

    def table_cell(
            self, text, col='', row='',
            is_last_row_item=False, has_child_list=False):
        if has_child_list:
            self.columns = {}
            self.columns['Column'] = self.col_count
            self.columns['list'] = True
            self.table_info.append(self.columns)
        if col:
            col = int(col)
            if not self.counted_columns and col:
                self.col_count += col
        elif not self.counted_columns:
            self.col_count += 1
        if row:
            row = int(row)
        slug = ''
        if col:
            slug += r'\multicolumn{%s}{c}' % col
        if row:
            slug += r'\multirow{%s}{*}' % row
        if self.line_break_in_table:
            slug += r'\parbox{20cm}'
        if text == '':
            slug += '{}'
        else:
            slug += '{' + text + '}'
        if is_last_row_item:
            slug += r' \\' + '\n'
            return slug
        self.line_break_in_table = False
        return '%s & ' % slug

    def page_break(self):
        return r'\newpage '

    def indent(self, text, alignment='', firstLine='',
               left='', right='', hanging='', is_in_table=False):
        if not is_in_table:
            slug = ''
            if hanging:
                hanging = float(hanging)
                hanging = hanging * float(3)/float(4)
                return r'\begin{hangparas}{%spt}{1} %s ' \
                       r'\end{hangparas}' % (hanging, text) + '\n'
            if right:
                right = float(right)
                right = right * float(3) / float(4)
            if left:
                left = float(left)
                left = left * float(3) / float(4)
            if left or right:
                slug += r'\begin{adjustwidth}{%s}{%s}' % (
                    left+'pt', right+'pt')
            if firstLine:
                slug += r'\setlength{\parindent}{'+firstLine+r'pt}\indent '
            if alignment:
                if alignment == 'left':
                    slug += r'\begin{flushright} %s \end{flushright}' % text
                elif alignment == 'center':
                    slug += r'\begin{center} %s \end{center}' % text
                elif alignment == 'right':
                    slug += r'\begin{flushleft} %s \end{flushleft}' % text
            if left or right:
                slug += r'\end{adjustwidth}'
            return slug
        else:
            self.columns = {}
            self.columns['Column'] = self.col_count
            self.columns['justify'] = alignment
            if self.columns not in self.table_info:
                self.table_info.append(self.columns)
            return text

    def break_tag(self, is_in_table):
        if is_in_table:
            self.line_break_in_table = True
        return r'\\'

    def deletion(self, text, author, date):
        return r'\deleted[id='+author+',remark='+date+']{%s}' % text

    def caps(self, text):
        return r'\MakeUppercase{%s}' % text

    def small_caps(self, text):
        return r'\textsx{%s}' % text

    def strike(self, text):
        return r'\sout{%s}' % text

    def hide(self, text):
        return r'\begin{comment}%s\end{comment}' % text

    def superscript(self, text):
        return r'\textsuperscript{%s}' % text

    def subscript(self, text):
        return r'\textsubscript{%s}' % text

    def empty_cell(self):
        return ' & '
