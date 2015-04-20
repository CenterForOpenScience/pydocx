# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.open_xml_part import OpenXmlPart


class StyleDefinitionsPart(OpenXmlPart):
    '''
    Represents style definitions within a Word document container.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.styledefinitionspart%28v=office.14%29.aspx  # noqa
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'styles',
    ])
