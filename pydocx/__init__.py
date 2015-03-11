from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import sys
import logging

from pydocx.parsers import Docx2Html, Docx2Markdown

__version__ = '0.4.3'


def docx2html(path):
    return Docx2Html(path).parsed


def docx2markdown(path):
    return Docx2Markdown(path).parsed


def convert(parser_type, docx_path, output_path):
    if parser_type == '--html':
        output = Docx2Html(docx_path).parsed
    elif parser_type == '--markdown':
        output = Docx2Markdown(docx_path).parsed
    else:
        print('Only valid parsers are --html and --markdown')
        sys.exit()
    with open(output_path, 'wb') as f:
        f.write(output.encode('utf-8'))


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        parser_type = sys.argv[1]
        docx_path = sys.argv[2]
        output_path = sys.argv[3]
    except IndexError:
        print('Usage: pydocx [--html|--markdown] input.docx output')
        sys.exit()

    convert(parser_type, docx_path, output_path)

if __name__ == '__main__':
    main()
