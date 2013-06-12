from .parsers import Docx2Html, Docx2Markdown
from HtmlConverter import Html2Docx

def docx2html(path):
    return Docx2Html(path).parsed


def docx2markdown(path):
    return Docx2Markdown(path).parsed

def html2docx(path):
    return Html2Docx(path).parsed


VERSION = '0.3.0'
