from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import posixpath
from collections import defaultdict


class OpenXmlPartContainer(object):
    '''
    Represents a container for other OpenXmlParts that are associated with a
    OpenXmlPackage.

    See also: http://msdn.microsoft.com/en-us/library/documentformat.openxml.packaging.openxmlpartcontainer%28v=office.14%29.aspx  # noqa
    '''

    child_part_types = []

    def __init__(self):
        self.external_relationships = {}
        self.hyperlink_relationships = {}
        self._parts = None
        self.parts_of_type = defaultdict(list)

    @property
    def parts(self):
        if self._parts is None:
            self._parts = {}
            self._load_parts()
        return self._parts

    def get_relationship_lookup(self):
        raise NotImplementedError

    def _load_parts(self):
        from pydocx.openxml.packaging.open_xml_package import OpenXmlPackage

        relationship_lookup = self.get_relationship_lookup()
        # TODO I don't like this -Kyle
        if isinstance(self, OpenXmlPackage):
            open_xml_package = self
        else:
            open_xml_package = self.open_xml_package
        for child_part_type in self.child_part_types:
            relationships = relationship_lookup.get_relationships_by_type(
                child_part_type.relationship_type,
            )
            if not relationships:
                continue
            for relationship in relationships:
                if relationship.is_external():
                    part_uri = relationship.target_uri
                else:
                    base, _ = posixpath.split(relationship.source_uri)
                    part_uri = posixpath.join(
                        base,
                        relationship.target_uri,
                    )
                    if not open_xml_package.package.part_exists(part_uri):
                        continue

                part = child_part_type(
                    open_xml_package=open_xml_package,
                    uri=part_uri,
                )
                self.add_part(
                    part=part,
                    relationship_id=relationship.relationship_id,
                )

    def _ensure_parts_are_loaded(self):
        return self.parts

    def get_parts_of_type(self, relationship_type):
        self._ensure_parts_are_loaded()
        return list(self.parts_of_type[relationship_type])

    def get_part_by_id(self, relationship_id):
        return self.parts[relationship_id]

    def get_part_of_class_type(self, part_class):
        self._ensure_parts_are_loaded()
        parts = self.get_parts_of_type(
            part_class.relationship_type,
        )
        if parts:
            return parts[0]

    def add_part(self, part, relationship_id=None):
        self._ensure_parts_are_loaded()
        if relationship_id is not None:
            self.parts[relationship_id] = part
        self.parts_of_type[part.relationship_type].append(part)
