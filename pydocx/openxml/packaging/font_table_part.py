# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.open_xml_part import OpenXmlPart


class FontTablePart(OpenXmlPart):
    '''
    Represents the fonts associated within a document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.fonttablepart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'fontTable',
    ])
