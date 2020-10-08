from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export import PyDocXHTMLExporter, PyDocXMarkdownExporter
from pydocx.util.xml import (
    check_mht
)

class PyDocX(object):
    @staticmethod
    def to_html(path_or_stream):
        mht_str = check_mht(path_or_stream)
        if len(mht_str) > 0:
            return mht_str
        return PyDocXHTMLExporter(path_or_stream).export()

    @staticmethod
    def to_markdown(path_or_stream):
        return PyDocXMarkdownExporter(path_or_stream).export()
