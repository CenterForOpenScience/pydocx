from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export import PyDocXHTMLExporter, PyDocXMarkdownExporter


class PyDocX(object):
    @staticmethod
    def to_html(path_or_stream):
        return PyDocXHTMLExporter(path_or_stream).export()

    @staticmethod
    def to_markdown(path_or_stream):
        return PyDocXMarkdownExporter(path_or_stream).export()
