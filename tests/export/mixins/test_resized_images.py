# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase
import os

from pydocx.export.html import PyDocXHTMLExporter
from pydocx.export.mixins import ResizedImagesExportMixin
from pydocx.test import utils


class PyDocXHTMLExporterWithResizedImages(
    ResizedImagesExportMixin,
    PyDocXHTMLExporter
):
    pass


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
            data = f.read()

            if img_name.endswith('.html'):
                data = data.decode()

            return data

    return file_path


class PyDocXHTMLExporterWithResizedImagesTestCase(TestCase):
    exporter = PyDocXHTMLExporterWithResizedImages

    def test_export_docx_to_resized_images(self):
        docx_file_path = get_fixture('png_basic_resize_linked_photo.docx')
        html_file_content = get_fixture(
            'png_basic_resize_linked_photo.html',
            as_binary=True
        )

        html = self.exporter(docx_file_path).parsed

        utils.assert_html_equal(html, html_file_content)
