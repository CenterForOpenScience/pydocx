from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import sys
import logging

from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.parsers.Docx2Markdown import Docx2Markdown


def convert(parser_type, docx_path, output_path):
    if parser_type == '--html':
        output = Docx2Html(docx_path).parsed
    elif parser_type == '--markdown':
        output = Docx2Markdown(docx_path).parsed
    else:
        print('Only valid parsers are --html and --markdown')
        return 2
    with open(output_path, 'wb') as f:
        f.write(output.encode('utf-8'))
    return 0


def usage():
    print('Usage: pydocx --html|--markdown input.docx output')
    return 1


def main(args=None):
    logging.basicConfig(level=logging.DEBUG)

    if args is None:
        return usage()

    try:
        parser_type = args[0]
        docx_path = args[1]
        output_path = args[2]
    except IndexError:
        return usage()

    return convert(parser_type, docx_path, output_path)

if __name__ == "__main__":
    sys.exit(main(args=sys.argv[1:]) or 0)
