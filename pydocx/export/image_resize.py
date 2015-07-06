# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import base64
from StringIO import StringIO
from urlparse import urlparse
import posixpath

import requests

from requests.exceptions import InvalidSchema

from pydocx.util import uri
from PIL import Image

IMAGE_EXTENSIONS_TO_SKIP = ['emf', 'wmf', 'svg']
IMAGE_FORMATS_TO_GIF_COMPRESS = ['BMP', 'TIFF']


class ImageResizer(object):
    def __init__(self, image_data, filename, x, y, skip_extensions=None):
        self.image_data = image_data
        self.filename = filename
        self.x = self._get_dimension(x)
        self.y = self._get_dimension(y)
        self.image_format = None
        self.image = None

        self.skip_extensions = IMAGE_EXTENSIONS_TO_SKIP

        if isinstance(skip_extensions, list):
            self.skip_extensions += skip_extensions

    def has_skipable_extension(self):
        if not self.filename:
            return False
        lower_src = self.filename.lower()
        extension = lower_src.rsplit('.')[-1]
        return extension in self.skip_extensions

    def has_height_and_width(self):
        return bool(self.x and self.y)

    def _get_dimension(self, dim):
        if not dim:
            return 0
        try:
            return int(dim.strip('px'))
        except ValueError as e:
            raise e

    def init_image(self):
        image_data = self.image_data
        match = uri.is_encoded_image_uri(image_data)
        if match:
            image_data = base64.b64decode(match.group('image_data'))
        try:
            self.image = Image.open(StringIO(image_data))
        except (IOError, SystemError) as e:
            # PIL can't open it, return the image_data as is.
            raise e

    def resize_image(self):
        # Let's not resize a base64 encoded image.
        if uri.is_encoded_image_uri(self.image_data):
            return
        if not self.image:
            return

        _resized = False

        image_format = self.image.format
        self.image_format = image_format
        expected_sizes = (self.x, self.y)

        current_area = self.x * self.y
        new_x, new_y = self.image.size
        new_area = new_x * new_y
        # We don't ever want to resize an image and it be larger than the
        # original. As such count the before and after pixels (area) and
        # compare.
        if (current_area < new_area) and (expected_sizes != self.image.size):
            try:
                self.image = self.image.resize(expected_sizes, Image.ANTIALIAS)
                _resized = True
            except (IOError, SystemError):
                # Image can't be resized, such is life.
                pass
        if image_format in IMAGE_FORMATS_TO_GIF_COMPRESS:
            # Convert to gif.
            image_format = 'GIF'
        output = StringIO()
        try:
            self.image.save(output, image_format)
            self.image_data = output.getvalue()
        except (IOError, SystemError) as e:
            # PIL can't save this image.
            raise e

        self.image_format = image_format

        return _resized

    def update_filename(self):
        if not self.image_format:
            return
        if not self.filename:
            return
        self.filename = uri.replace_extension(
            self.filename,
            self.image_format.lower(),
        )


def get_image_data_and_filename(image_data_or_url, filename):
    """
    If the image is an external image then the image_data is actually a link to
    the image and the filename is likely garbage.
    """

    parsed_url = urlparse(image_data_or_url)

    _, real_filename = posixpath.split(parsed_url.path)

    match = uri.is_encoded_image_uri(image_data_or_url)

    sanitized_filename = None

    if not match:
        sanitized_filename = uri.sanitize_filename(real_filename)

    real_image_data = get_image_from_src(image_data_or_url)

    if real_image_data is None:
        return image_data_or_url, filename

    return real_image_data, sanitized_filename


def get_image_from_src(src):
    """
    Take a src attribute from an image tag and return the content image data
    associated with that image. At the minimum we should handle https:// and
    base64 encoded images.
    """
    # Handle the easy case first, its an external link to somewhere else.
    try:
        response = requests.get(src)
    except InvalidSchema:
        pass
    else:
        return response.content

    # Check to see if it's a base64 encoded image.
    match = uri.is_encoded_image_uri(src)
    if match:
        return src

    # Not really sure what is going on here, punt for now.
    return src
