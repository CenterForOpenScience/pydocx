from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import base64
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from nose.tools import raises

from pydocx.tests import (
    assert_html_equal,
    html_is_equal,
    prettify,
    BASE_HTML,
)
from pydocx.parsers.Docx2Html import Docx2Html
from pydocx.utils import ZipFile
from pydocx.exceptions import MalformedDocxException


def convert(path, *args, **kwargs):
    return Docx2Html(path, *args, **kwargs).parsed


class ConvertDocxToHtmlTestCase(TestCase):
    cases_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
    )

    cases = (
        'simple',
        'nested_lists',
        'simple_lists',
        'inline_tags',
        'all_configured_styles',
        'special_chars',
        'table_col_row_span',
        'nested_table_rowspan',
        'nested_tables',
        'list_in_table',
        'tables_in_lists',
        'track_changes_on',
        'headers',
        'split_header',
        'lists_with_styles',
        'has_title',
        'simple_table',
        'justification',
        'missing_style',
        'missing_numbering',
        'styled_bolding',
        'no_break_hyphen',
        'shift_enter',
        # In the expected HTML output for "list_to_header", the list element
        # GGG is expected to be "upperRoman". This is showing that only top
        # level upperRomans are converted.
        'list_to_header',
        'has_missing_image',
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
    assert_html_equal(actual_html, BASE_HTML % '''
        <p>
            AAA
            <img src="data:image/gif;base64,%s" height="55px" width="260px" />
        </p>
    ''' % image_data)


def test_local_dpi():
    # The image in this file does not have a set height or width, show that the
    # html will generate without it.
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'localDpi.docx',
    )
    actual_html = convert(file_path)
    image_data = get_image_data(file_path, 'image1.jpeg')
    assert_html_equal(actual_html, BASE_HTML % '''
        <p><img src="data:image/jpeg;base64,%s" /></p>
    ''' % image_data)


@raises(MalformedDocxException)
def test_malformed_docx_exception():
    with NamedTemporaryFile(suffix='.docx') as f:
        convert(f.name)
