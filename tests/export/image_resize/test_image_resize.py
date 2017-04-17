# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import os
from unittest import TestCase

from pydocx.export.image_resize import (
    get_image_data_and_filename,
    get_image_from_src,
    ImageResizer,
)
from PIL import Image
from pydocx.util import get_stream_cls


def get_img(img_name, as_binary=False):
    file_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..',
        '..',
        'fixtures',
        'images',
        img_name,
    )

    if as_binary:
        with open(file_path, 'rb') as f:
            data = f.read()

            if img_name.endswith('.data'):
                data = data.decode()

            return data


class GetImageFromSrcTestCase(TestCase):
    def test_get_image_from_src_url(self):
        web_data = get_image_from_src('http://httpbin.org/image/png')
        local_data = get_img('image1.png', as_binary=True)

        self.assertEqual(web_data, local_data)

    def test_get_image_from_src_data(self):
        img_data = get_img('image1.data', as_binary=True)
        result = get_image_from_src(img_data)

        self.assertEqual(img_data, result)


class GetImageDataAndFileNameTestCase(TestCase):
    def test_get_image_from_src_url(self):
        uri = 'http://httpbin.org/image/png'
        img_data, filename = get_image_data_and_filename(uri, 'png.png')

        self.assertEqual(img_data, img_data)
        self.assertEqual(filename, 'png')


class ImageResizerTestCase(TestCase):
    def test_init_object(self):
        image_data = get_img('image1.png', as_binary=True)
        ir = ImageResizer(image_data, 'image1.png', '100 px', '100 px')

        self.assertTrue(ir)

    def test_has_skipable_extension_true(self):
        image_data = get_img('image1.png', as_binary=True)
        ir = ImageResizer(
            image_data,
            'image1.png',
            '100 px',
            '100 px',
            skip_extensions=['png']
        )

        self.assertTrue(ir.has_skippable_extension())

    def test_has_skipable_extension_false(self):
        image_data = get_img('image1.png', as_binary=True)
        ir = ImageResizer(image_data, 'image1.png', '100 px', '100 px')

        self.assertFalse(ir.has_skippable_extension())

    def test_has_height_and_width_true(self):
        image_data = get_img('image1.png', as_binary=True)
        ir = ImageResizer(image_data, 'image1.png', '10 px', '20 px')

        self.assertTrue(ir.has_height_and_width())

    def test_has_height_and_width_false(self):
        image_data = get_img('image1.png', as_binary=True)

        ir = ImageResizer(image_data, 'image1.png', '0 px', '10 px')
        self.assertFalse(ir.has_height_and_width())

        ir = ImageResizer(image_data, 'image1.png', '10 px', '0 px')
        self.assertFalse(ir.has_height_and_width())

        ir = ImageResizer(image_data, 'image1.png', '0 px', '0 px')
        self.assertFalse(ir.has_height_and_width())

    def test_init_image(self):
        image_data = get_img('image1.png', as_binary=True)
        ir = ImageResizer(image_data, 'image1.png', '100 px', '100 px')
        ir.init_image()

        self.assertEqual(ir.image, Image.open(get_stream_cls(image_data)(image_data)))

    def test_init_image_with_data_should_be_the_same(self):
        image_data = get_img('image1.data', as_binary=True)
        png_data = get_img('image1.png', as_binary=True)

        ir = ImageResizer(image_data, 'image1.png', '100 px', '100 px')
        ir.init_image()

        png_image = Image.open(get_stream_cls(png_data)(png_data))
        self.assertEqual(ir.image, png_image)

    def test_init_image_exception(self):
        ir = ImageResizer(b'test_data3434', 'image1.png', '100 px', '100 px')

        self.assertRaises(IOError, ir.init_image)

    def test_resize_image_skip(self):
        image_data = get_img('image1.data', as_binary=True)

        ir = ImageResizer(image_data, 'image1.png', '48 px', '48 px')
        ir.init_image()

        result = ir.resize_image()

        self.assertFalse(result)

    def test_resize_image_success(self):
        image_data = get_img('image1.png', as_binary=True)

        ir = ImageResizer(image_data, 'image1.png', '48 px', '48 px')
        ir.init_image()

        result = ir.resize_image()

        self.assertTrue(result)

        self.assertEqual(ir.image.size, (48, 48))

    def test_resize_image_keep_original(self):
        image_data = get_img('image1.png', as_binary=True)

        ir = ImageResizer(image_data, 'image1.png', '100 px', '100 px')

        ir.init_image()

        result = ir.resize_image()

        self.assertFalse(result)

        self.assertEqual(ir.image.size, (100, 100))

    def test_resize_image_change_to_gif(self):
        image_data = get_img('image2.tif', as_binary=True)

        ir = ImageResizer(image_data, 'image2.tif', '50 px', '50 px')

        ir.init_image()
        result = ir.resize_image()

        self.assertTrue(result)

        self.assertEqual(ir.image_format, 'GIF')

        input = get_stream_cls(image_data)(image_data)
        image = Image.open(input).resize(
            (50, 50),
            Image.ANTIALIAS
        )

        self.assertEqual(image, ir.image)
        self.assertEqual('image2.tif', ir.filename)

    def test_update_filename(self):
        image_data = get_img('image1.png', as_binary=True)

        ir = ImageResizer(image_data, 'image1.png', '48 px', '48 px')

        ir.init_image()

        ir.update_filename()

        self.assertEqual(ir.filename, 'image1.png')

    def test_update_filename_to_gif(self):
        image_data = get_img('image2.tif', as_binary=True)

        ir = ImageResizer(image_data, 'image2.tif', '48 px', '48 px')

        ir.init_image()
        ir.resize_image()

        ir.update_filename()

        self.assertEqual(ir.filename, 'image2.gif')
