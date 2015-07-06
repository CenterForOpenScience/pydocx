# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from unittest import TestCase
from pydocx.util import uri


class UriTestCase(TestCase):
    def test_uri_is_external(self):
        self.assertTrue(uri.uri_is_external('http://example.com'))
        self.assertTrue(uri.uri_is_external('https://example.com'))
        self.assertTrue(uri.uri_is_external('https://example.com'))

    def test_uri_is_internal(self):
        self.assertTrue(uri.uri_is_internal('/assets/'))
        self.assertTrue(uri.uri_is_internal('/assets/logo.png'))

    def test_is_encoded_image_uri_true(self):
        image_data = 'data:image/png;base64,iVBOR='

        self.assertTrue(uri.is_encoded_image_uri(image_data))
        self.assertFalse(uri.is_encoded_image_uri('data:image/png;base64,'))
        self.assertFalse(uri.is_encoded_image_uri('http://example.com/logo.png'))

        self.assertEqual({'image_data': 'iVBOR=', 'extension': 'png'},
                         uri.is_encoded_image_uri(image_data).groupdict())

    def test_replace_extension(self):
        self.assertEqual('one/two/three.four.html',
                         uri.replace_extension('one/two/three.four.doc', '.html')
                         )

        self.assertEqual('one/two/three.four.doc',
                         uri.replace_extension('one/two/three.four.doc', '.doc')
                         )

    def test_sanitize_filename(self):
        self.assertEqual(uri.sanitize_filename('1409764011-image1.gif'), 'image1.gif')
        self.assertEqual(uri.sanitize_filename('409764011-image1.gif'), '409764011-image1.gif')
        self.assertEqual(uri.sanitize_filename('409764011-image.gif'), '409764011-image.gif')
        self.assertEqual(uri.sanitize_filename('image%20%232014.gif'), 'image #2014.gif')
