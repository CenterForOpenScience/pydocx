# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.openxml.wordprocessing import Run


class RunTestCase(TestCase):
    def test_can_instantiate_empty_object(self):
        run = Run()
        assert run

    def test_effective_properties_is_memoized(self):
        run = Run()
        effective_properties = run.effective_properties
        sentinel = object()
        effective_properties.bold = sentinel
        self.assertEqual(run.effective_properties.bold, sentinel)
