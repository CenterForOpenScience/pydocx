# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.OpenXmlPart import OpenXmlPart


class FootnotesPart(OpenXmlPart):
    '''
    Represents a Footnotes part within a Word document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.footnotespart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'footnotes',
    ])
