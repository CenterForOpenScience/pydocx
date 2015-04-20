# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.open_xml_part import OpenXmlPart


class NumberingDefinitionsPart(OpenXmlPart):
    '''
    Represents the list numbering definitions within a document container.
    '''

    relationship_type = '/'.join([
        'http://schemas.openxmlformats.org',
        'officeDocument',
        '2006',
        'relationships',
        'numbering',
    ])
