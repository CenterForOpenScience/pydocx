from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import base64
import os
from tempfile import NamedTemporaryFile

from nose.tools import raises

from pydocx.exceptions import MalformedDocxException
from pydocx.export.html import PyDocXHTMLExporter
from pydocx.test.testcases import BASE_HTML, DocXFixtureTestCaseFactory
from pydocx.test.utils import assert_html_equal
from pydocx.util.zip import ZipFile


def convert(path, *args, **kwargs):
    exporter = PyDocXHTMLExporter(path, *args, **kwargs)
    return exporter.export()


class ConvertDocxToHtmlTestCase(DocXFixtureTestCaseFactory):
    cases = (
        'read_same_image_multiple_times',
        'all_configured_styles',
        'has_title',
        'inline_tags',
        'has_missing_image',
        'justification',
        'list_in_table',
        'external_image',
        'export_from_googledocs',
        'has_missing_image',
        'lists_with_styles',
        'missing_numbering',
        'missing_style',
        'nested_lists',
        'nested_table_rowspan',
        'nested_tables',
        'no_break_hyphen',
        'shift_enter',
        'simple',
        'simple_lists',
        'simple_table',
        'special_chars',
        'styled_bolding',
        'table_col_row_span',
        'tables_in_lists',
        'track_changes_on',
        'table_with_multi_rowspan'
    )

    @raises(MalformedDocxException)
    def test_raises_malformed_when_relationships_are_missing(self):
        docx_path = self.get_path_to_fixture('missing_relationships.docx')
        self.convert_docx_to_html(docx_path)

    def test_unicode(self):
        docx_path = self.get_path_to_fixture('greek_alphabet.docx')
        actual_html = self.convert_docx_to_html(docx_path)
        assert actual_html is not None
        assert '\u0391\u03b1' in actual_html

    def test_result_from_file_pointer_matches_result_from_path(self):
        path = self.get_path_to_fixture('simple.docx')
        path_html = self.convert_docx_to_html(path)
        file_html = self.convert_docx_to_html(open(path, 'rb'))
        assert file_html
        self.assertEqual(path_html, file_html)


ConvertDocxToHtmlTestCase.generate()


def get_image_data(docx_file_path, image_name):
    """
    Return base 64 encoded data for the image_name that is stored in the
    docx_file_path.
    """
    with ZipFile(docx_file_path) as f:
        images = [
            e for e in f.infolist()
            if e.filename == 'word/media/%s' % image_name
        ]
        if not images:
            raise AssertionError('%s not in %s' % (image_name, docx_file_path))
        data = f.read(images[0].filename)
    return base64.b64encode(data).decode()


def test_has_image():
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'has_image.docx',
    )

    actual_html = convert(file_path)
    image_data = get_image_data(file_path, 'image1.gif')
    expected_html = BASE_HTML % '''
        <p>
            AAA
            <img
                height="55px"
                src="data:image/gif;base64,{data}"
                width="260px"
            />
        </p>
    '''.format(data=image_data)
    assert_html_equal(actual_html, expected_html)


@raises(MalformedDocxException)
def test_malformed_docx_exception():
    with NamedTemporaryFile(suffix='.docx') as f:
        convert(f.name)
