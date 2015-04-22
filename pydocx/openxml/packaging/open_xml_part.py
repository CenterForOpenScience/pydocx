# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.openxml.packaging.open_xml_part_container import OpenXmlPartContainer  # noqa
from pydocx.util.xml import parse_xml_from_string


class OpenXmlPart(OpenXmlPartContainer):
    '''
    An OpenXmlPart is a part associated with either another OpenXmlPart or an
    OpenXmlPackage.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.openxmlpart%28v=office.14%29.aspx  # noqa
    '''

    def __init__(
        self,
        uri,
        open_xml_package,
    ):
        super(OpenXmlPart, self).__init__()
        self._root_element = None
        self.uri = uri
        self.open_xml_package = open_xml_package

    @property
    def root_element(self):
        if self._root_element is None:
            if self.stream is None:
                return
            data = self.stream.read()
            self._root_element = parse_xml_from_string(
                xml=data,
                remove_namespaces=True,
            )
        return self._root_element

    @property
    def package_part(self):
        return self.open_xml_package.package.get_part(self.uri)

    @property
    def stream(self):
        part = self.package_part
        if part:
            return part.stream
