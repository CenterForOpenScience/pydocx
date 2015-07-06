# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.export.html import PyDocXHTMLExporterWithImageResize
from unittest import TestCase
import os
from pydocx.test import utils


def get_fixture(img_name, as_binary=False):
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        '..',
        'fixtures',
        'images',
        img_name,
    )

    if as_binary:
        with open(file_path, 'rb') as f:
            return f.read()

    return file_path


class PyDocXHTMLExporterWithImageResizeTestCase(TestCase):
    exporter = PyDocXHTMLExporterWithImageResize

    def test_export_docx_to_html_image_resize(self):
        docx_file_path = get_fixture('png_basic_resize_linked_photo.docx')
        html_file_content = get_fixture('png_basic_resize_linked_photo.html', as_binary=True)

        html = self.exporter(docx_file_path).parsed

        utils.assert_html_equal(html, html_file_content)
