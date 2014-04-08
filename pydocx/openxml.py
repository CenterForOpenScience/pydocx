from __future__ import absolute_import

from collections import defaultdict
from xml.etree import cElementTree

from pydocx.packaging import ZipPackage


class OpenXmlPartContainer(object):
    def __init__(self):
        self.external_relationships = {}
        self.hyperlink_relationships = {}
        self._parts = None
        self.parts_of_type = defaultdict(list)

    @property
    def parts(self):
        if self._parts is None:
            self._parts = {}
            self.load_parts()
        return self._parts

    def load_parts(self):
        raise NotImplementedError

    def ensure_parts_are_loaded(self):
        return self.parts

    def get_parts_of_type(self, relationship_type):
        self.ensure_parts_are_loaded()
        return list(self.parts_of_type[relationship_type])

    def get_part_by_id(self, relationship_id):
        return self.parts[relationship_id]

    def add_part(self, part, relationship_id=None):
        self.ensure_parts_are_loaded()
        if relationship_id is not None:
            self.parts[relationship_id] = part
        self.parts_of_type[part.relationship_type].append(part)


class OpenXmlPart(OpenXmlPartContainer):
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
            self._root_element = cElementTree.fromstring(self.stream.read())
        return self._root_element

    @property
    def stream(self):
        part = self.open_xml_package.package.get_part(self.uri)
        return part.stream


class OpenXmlPackage(OpenXmlPartContainer):
    def __init__(self, path):
        super(OpenXmlPackage, self).__init__()
        self.package = ZipPackage(path=path)
