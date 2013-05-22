from .parsers import Docx2LaTex

def docx2latex(path):
    return Docx2LaTex(path).parsed