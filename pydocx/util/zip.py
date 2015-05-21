from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import zipfile
from contextlib import contextmanager
from io import BytesIO

from pydocx.exceptions import MalformedDocxException


@contextmanager
def ZipFile(path, mode='r'):  # This is not needed in python 3.2+
    try:
        f = zipfile.ZipFile(path, mode)
    except zipfile.BadZipfile:
        raise MalformedDocxException('Passed in document is not a docx')
    yield f
    f.close()


def create_zip_archive(paths_to_data):
    '''
    Return an in-memory zip archive.

    `paths_to_data` (dictionary) - For each key, value, the key is treated as a
    path within the zip archive. The value is the data that will be stored at
    that path specified by the key.

    Each path MUST NOT include an initial '/'. Each path MUST use '/' as a file
    separator (this is requried by the zip specification).

    paths_to_data = {
        'path/file.txt': 'hello',
    }
    '''
    archive = BytesIO()
    with ZipFile(archive, 'w') as zf:
        for arcname, data in paths_to_data.items():
            if data is None:
                continue
            zf.writestr(arcname, data.encode('utf-8'))
    return archive
