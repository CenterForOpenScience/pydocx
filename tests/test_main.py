from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

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
