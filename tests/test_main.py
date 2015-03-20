from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from tempfile import NamedTemporaryFile
from unittest import TestCase

from nose import SkipTest

from pydocx.test.testcases import BASE_HTML
from pydocx.test.utils import assert_html_equal
from pydocx.__main__ import main


class MainTestCase(TestCase):
    def test_return_code_with_no_args(self):
        result = main()
        self.assertEqual(result, 1)

    def test_return_code_with_one_args(self):
        result = main(['foo'])
        self.assertEqual(result, 1)

    def test_return_code_with_two_args(self):
        result = main(['foo', 'bar'])
        self.assertEqual(result, 1)

    def test_return_code_with_three_args(self):
        result = main(['foo', 'bar', 'baz'])
        self.assertEqual(result, 2)

    def test_convert_to_html_status_code(self):
        with NamedTemporaryFile() as f:
            result = main([
                '--html',
                'tests/fixtures/inline_tags.docx',
                f.name,
            ])
        self.assertEqual(result, 0)

    def test_convert_to_markdown_status_code(self):
        with NamedTemporaryFile() as f:
            result = main([
                '--markdown',
                'tests/fixtures/inline_tags.docx',
                f.name,
            ])
        self.assertEqual(result, 0)

    def test_convert_to_html_result(self):
        fixture_html = open('tests/fixtures/inline_tags.html').read()
        expected_html = BASE_HTML % fixture_html
        with NamedTemporaryFile() as f:
            result = main([
                '--html',
                'tests/fixtures/inline_tags.docx',
                f.name,
            ])
            data = open(f.name).read()
            assert_html_equal(data, expected_html)
        self.assertEqual(result, 0)

    def test_convert_to_markdown_result(self):
        raise SkipTest('Fixture files for markdown do not exist yet')
