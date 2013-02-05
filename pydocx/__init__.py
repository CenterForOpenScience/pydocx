from .parsers import *

def docx2html(path):
    return Docx2Html(path).parsed

def docx2markdown(path):
    return Docx2Markdown(path).parsed

