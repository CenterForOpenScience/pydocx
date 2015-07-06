from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export import PyDocXHTMLExporter, PyDocXMarkdownExporter, \
    PyDocXHTMLExporterWithImageResize


class PyDocX(object):
    @staticmethod
    def to_html(path_or_stream, image_resize=False):
        if image_resize:
            exporter_cls = PyDocXHTMLExporterWithImageResize
        else:
            exporter_cls = PyDocXHTMLExporter

        return exporter_cls(path_or_stream).parsed

    @staticmethod
    def to_markdown(path_or_stream):
        return PyDocXMarkdownExporter(path_or_stream).parsed
