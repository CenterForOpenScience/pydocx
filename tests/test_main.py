from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.__main__ import main


class MainTestCase(TestCase):
    def test_return_code_with_no_arguments(self):
        result = main()
        self.assertEqual(result, 1)
