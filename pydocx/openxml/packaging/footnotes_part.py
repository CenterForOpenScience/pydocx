# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.open_xml_part import OpenXmlPart
from pydocx.openxml.wordprocessing import Footnotes


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

    def __init__(self, *args, **kwargs):
        super(FootnotesPart, self).__init__(*args, **kwargs)
        self._footnotes = None

    @property
    def footnotes(self):
        if not self._footnotes:
            self._footnotes = self.load_footnotes()
        return self._footnotes

    def load_footnotes(self):
        self._footnotes = Footnotes.load(self.root_element, container=self)
        return self._footnotes
