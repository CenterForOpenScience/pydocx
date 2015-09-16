# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Hyperlink


class HyperlinkTestCase(TestCase):
    def test_target_uri_is_None_by_default(self):
        link = Hyperlink()
        self.assertEqual(link.target_uri, None)

    def test_target_uri_can_be_set_manually(self):
        link = Hyperlink()
        link.target_uri = 'foo'
        self.assertEqual(link.target_uri, 'foo')
