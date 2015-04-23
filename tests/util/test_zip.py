# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pydocx.exceptions import MalformedDocxException
from pydocx.util.zip import ZipFile, BytesIO


class ZipFileTestCase(TestCase):
    def test_with_bad_zip_file_raises_MalformedDocxException(self):
        archive = BytesIO(b'foo')
        try:
            with ZipFile(archive):
                pass
            raise AssertionError('Excepted MalformedDocxException')
        except MalformedDocxException:
            pass
