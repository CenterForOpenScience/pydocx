from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import base64
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from pydocx.exceptions import MalformedDocxException
from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.util.zip import ZipFile

from nose.tools import raises

from pydocx.test.testcases import BASE_HTML
from pydocx.test.utils import (
    assert_html_equal,
    html_is_equal,
    prettify,
)


def convert(path, *args, **kwargs):
    return Docx2Html(path, *args, **kwargs).parsed


class ConvertDocxToHtmlTestCase(TestCase):
    cases_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'fixtures',
    )

    cases = (
        'all_configured_styles',
        'has_title',
        'inline_tags',
        'has_missing_image',
        'justification',
        'list_in_table',
        # In the expected HTML output for "list_to_header", the list element
        # GGG is expected to be "upperRoman". This is showing that only top
        # level upperRomans are converted.
        'external_image',
        'export_from_googledocs',
        'fake_subscript',
        'fake_superscript',
        'has_missing_image',
        'list_to_header',
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
        'split_header',
        'styled_bolding',
        'table_col_row_span',
        'tables_in_lists',
        'track_changes_on',
    )

    @classmethod
    def create(cls, name):
        def run_test(self):
            docx_path = self.get_path_to_fixture('%s.docx' % name)
            expected_path = self.get_path_to_fixture('%s.html' % name)

            expected = ''
            with open(expected_path) as f:
                expected = f.read()

            expected = BASE_HTML % expected
            result = self.convert_docx_to_html(
                docx_path,
                convert_root_level_upper_roman=True,
            )
            self.assertHtmlEqual(result, expected)
        return run_test

    @classmethod
    def generate(cls):
        for case in cls.cases:
            test_method = cls.create(case)
            name = str('test_%s' % case)
            test_method.__name__ = name
            setattr(cls, name, test_method)

    def convert_docx_to_html(self, path_to_docx, *args, **kwargs):
        return Docx2Html(path_to_docx, *args, **kwargs).parsed

    def assertHtmlEqual(self, actual, expected):
        if not html_is_equal(actual, expected):
            actual = prettify(actual)
            message = 'The expected HTML did not match the actual HTML:'
            raise AssertionError(message + '\n' + actual)

    def get_path_to_fixture(self, fixture):
        return os.path.join(self.cases_path, fixture)

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
        'fixtures',
        'has_image.docx',
    )

    actual_html = convert(file_path)
    image_data = get_image_data(file_path, 'image1.gif')
    assert_html_equal(actual_html, BASE_HTML % '''
        <p>
            AAA
            <img src="data:image/gif;base64,%s" height="55px" width="260px" />
        </p>
    ''' % image_data)


@raises(MalformedDocxException)
def test_malformed_docx_exception():
    with NamedTemporaryFile(suffix='.docx') as f:
        convert(f.name)
