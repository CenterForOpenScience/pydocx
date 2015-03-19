from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import sys

from pydocx.parsers import Docx2Html, Docx2Markdown


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


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        parser_type = args[1]
        docx_path = args[2]
        output_path = args[3]
    except IndexError:
        print('Usage: pydocx [--html|--markdown] input.docx output')
        return 1

    return convert(parser_type, docx_path, output_path)

if __name__ == "__main__":
    sys.exit(main() or 0)
