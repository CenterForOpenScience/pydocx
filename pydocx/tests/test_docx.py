from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import base64
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from nose.plugins.skip import SkipTest
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


def test_has_image_using_image_handler():
    raise SkipTest('This needs to be converted to an xml test')
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'has_image.docx',
    )

    def image_handler(*args, **kwargs):
        return 'test'
    actual_html = convert(file_path)
    assert_html_equal(actual_html, BASE_HTML % '''
        <p>AAA<img src="test" height="55" width="260" /></p>
    ''')


def test_headers_with_full_line_styles():
    raise SkipTest('This test is not yet passing')
    # Show that if a natural header is completely bold/italics that
    # bold/italics will get stripped out.
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'headers_with_full_line_styles.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, BASE_HTML % '''
        <h2>AAA</h2>
        <h2>BBB</h2>
        <h2><strong>C</strong><em>C</em>C</h2>
    ''')


def test_convert_p_to_h():
    raise SkipTest('This test is not yet passing')
    # Show when it is correct to convert a p tag to an h tag based on
    # bold/italics
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'convert_p_to_h.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, BASE_HTML % '''
        <h2>AAA</h2>
        <h2>BBB</h2>
        <p>CCC</p>
        <ol list-style-type="decimal">
            <li><strong>DDD</strong></li>
            <li><em>EEE</em></li>
            <li>FFF</li>
        </ol>
        <table border="1">
            <tr>
                <td><strong>GGG</strong></td>
                <td><em>HHH</em></td>
            </tr>
            <tr>
                <td>III</td>
                <td>JJJ</td>
            </tr>
        </table>
    ''')


def test_fake_headings_by_length():
    raise SkipTest('This test is not yet passing')
    # Show that converting p tags to h tags has a length limit. If the p tag is
    # supposed to be converted to an h tag but has more than seven words in the
    # paragraph do not convert it.
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'fake_headings_by_length.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, BASE_HTML % '''
        <h2>Heading.</h2>
        <h2>Still a heading.</h2>
        <p>
        <strong>This is not a heading because it is too many words.</strong>
        </p>
    ''')


def test_upper_alpha_all_bold():
    raise SkipTest('This test is not yet passing')
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        'fixtures',
        'upper_alpha_all_bold.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, BASE_HTML % '''
        <h2>AAA</h2>
        <h2>BBB</h2>
        <h2>CCC</h2>
    ''')


@raises(MalformedDocxException)
def test_malformed_docx_exception():
    with NamedTemporaryFile(suffix='.docx') as f:
        convert(f.name)


def _converter(*args, **kwargs):
    # Having a converter that does nothing is the same as if abiword fails to
    # convert.
    pass


# def test_converter_broken():
#    file_path = 'test.doc'
#    assert_raises(
#        ConversionFailed,
#        lambda: convert(file_path, converter=_converter),
#    )


def test_fall_back():
    raise SkipTest('This test is not yet passing')
    file_path = 'test.doc'

    def fall_back(*args, **kwargs):
        return 'success'
    html = convert(file_path, fall_back=fall_back, converter=_converter)
    assert html == 'success'


# @mock.patch('docx2html.core.read_html_file')
# @mock.patch('docx2html.core.get_zip_file_handler')
# def test_html_files(patch_zip_handler, patch_read):
def test_html_files():
    raise SkipTest('This test is not yet passing')

    def raise_assertion(*args, **kwargs):
        raise AssertionError('Should not have called get_zip_file_handler')
    # patch_zip_handler.side_effect = raise_assertion

    def return_text(*args, **kwargs):
        return 'test'
    # patch_read.side_effect = return_text

    # Try with an html file
    file_path = 'test.html'

    html = convert(file_path)
    assert html == 'test'

    # Try again with an htm file.
    file_path = 'test.htm'

    html = convert(file_path)
    assert html == 'test'
