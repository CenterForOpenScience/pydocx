import zipfile

from .parsers import *
from .DocxParser import DocxParser

def get_document(path):
    document = None
    with zipfile.ZipFile(path) as f:
        document = f.read('word/document.xml')
    return document

def docx2html(path):
    return Docx2Html(get_document(path)).parsed

def docx2markdown(path):
    return Docx2Markdown(get_document(path)).parsed

