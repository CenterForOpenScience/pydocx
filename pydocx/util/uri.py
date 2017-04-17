from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import re
import os
# Support Python 2 and 3
try:
    from urllib.parse import unquote
except ImportError:
    from urlparse import unquote


IMAGE_DATA_URI_REGEX = re.compile(
    'data:image/(?P<extension>\w+);base64,(?P<image_data>.+)',
)


def uri_is_internal(uri):
    return uri.startswith('/')


def uri_is_external(uri):
    return not uri_is_internal(uri)


def is_encoded_image_uri(image_data):
    try:
        return IMAGE_DATA_URI_REGEX.match(image_data)
    except TypeError:
        return None


def replace_extension(file_path, new_ext):
    if not new_ext.startswith(os.extsep):
        new_ext = os.extsep + new_ext
    index = file_path.rfind(os.extsep)
    return file_path[:index] + new_ext


def sanitize_filename(filename):
    """
    When we create attachments from pydocx we usually add a timestamp followed
    by a dash (-) to make the image unique for round-tripping. In an effort to
    prevent a bunch of timestamps preceding the image name (in the event a
    document is round-tripped several times), strip off the timestamp
    and dash. When images come from docx they are always `image\d+`. We only
    want to strip off the timestamp and dash if they were programmatically
    added.
    """

    # (timestamp)-image(image_number).(file_extension)
    regex = re.compile('\d{10}-image\d+\.\w{3,4}')
    if regex.match(filename):
        _, filename = filename.rsplit('-', 1)
    return unquote(filename)
