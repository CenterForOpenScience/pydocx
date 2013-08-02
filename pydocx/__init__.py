from .parsers import Docx2Html, Docx2Markdown


def docx2html(path):
    return Docx2Html(path).parsed


def docx2markdown(path):
    return Docx2Markdown(path).parsed

VERSION = '0.3.9'
