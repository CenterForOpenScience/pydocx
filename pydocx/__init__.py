from .parsers import Docx2LaTex, Docx2Html, Docx2Markdown


def docx2html(path):
    return Docx2Html(path).parsed


def docx2markdown(path):
    return Docx2Markdown(path).parsed

<<<<<<< HEAD

def docx2latex(path):
    return Docx2LaTex(path).parsed

=======
>>>>>>> table_fix
VERSION = '0.3.1'
