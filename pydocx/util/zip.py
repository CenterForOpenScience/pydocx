from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import zipfile
from contextlib import contextmanager

from pydocx.exceptions import MalformedDocxException


@contextmanager
def ZipFile(path, mode='r'):  # This is not needed in python 3.2+
    try:
        f = zipfile.ZipFile(path, mode)
    except zipfile.BadZipfile:
        raise MalformedDocxException('Passed in document is not a docx')
    yield f
    f.close()
