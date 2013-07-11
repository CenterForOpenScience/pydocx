from .parsers import Docx2LaTex, Docx2Html, Docx2Markdown
from HtmlConversion import Html2Docx


def docx2html(path):
    return Docx2Html(path).parsed

def docx2markdown(path):
    return Docx2Markdown(path).parsed


def docx2latex(path):
    return Docx2LaTex(path).parsed

VERSION = '0.3.6'
