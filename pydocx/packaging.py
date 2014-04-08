from __future__ import absolute_import

import zipfile
from collections import defaultdict
from os.path import split as path_split
from xml.etree import cElementTree

from pydocx.exceptions import MalformedDocxException
from pydocx.utils import (
    xml_tag_split,
    zip_path_join,
)
from pydocx.xml import XmlNamespaceManager


class PackageRelationship(object):
    TARGET_MODE_INTERNAL = 'Internal'
    TARGET_MODE_EXTERNAL = 'External'

    def __init__(
        self,
        source_uri,
        target_uri,
        target_mode,
        relationship_type,
        relationship_id=None,
    ):
        super(PackageRelationship, self).__init__()
        self.source_uri = source_uri
        self.target_uri = target_uri
        self.target_mode = target_mode
        self.relationship_type = relationship_type
        self.relationship_id = relationship_id

    def is_internal(self):
        return self.target_mode == PackageRelationship.TARGET_MODE_INTERNAL

    def is_external(self):
        return self.target_mode == PackageRelationship.TARGET_MODE_EXTERNAL


class RelationshipManager(object):
    namespace = '/'.join([
        'http://schemas.openxmlformats.org',
        'package',
        '2006',
        'relationships',
    ])

    XML_TAG_NAME = 'Relationship'
    XML_ATTR_ID = 'Id'
    XML_ATTR_TARGETMODE = 'TargetMode'
    XML_ATTR_TARGET = 'Target'
    XML_ATTR_TYPE = 'Type'

    def __init__(self):
        super(RelationshipManager, self).__init__()
        self._relationships = None
        self.relationships_by_type = defaultdict(list)

    @property
    def relationships(self):
        if self._relationships is None:
            self._relationships = {}
            self.load_relationships()
        return self._relationships

    def ensure_relationships_are_loaded(self):
        return self.relationships

    def get_relationships_by_type(self, relationship_type):
        self.ensure_relationships_are_loaded()
        return list(self.relationships_by_type[relationship_type])

    def get_relationship(self, relationship_id):
        return self.relationships[relationship_id]

    def create_relationship(
        self,
        target_uri,
        target_mode,
        relationship_type,
        relationship_id=None,
    ):
        self.ensure_relationships_are_loaded()
        relationship = PackageRelationship(
            source_uri=self.uri,
            target_uri=target_uri,
            target_mode=target_mode,
            relationship_type=relationship_type,
            relationship_id=relationship_id,
        )
        if relationship_id:
            self.relationships[relationship_id] = relationship
        self.relationships_by_type[relationship_type].append(relationship)

    def get_part_container(self):
        raise NotImplementedError

    def load_relationships(self):
        part_container = self.get_part_container()
        if not part_container.part_exists(self.relationship_uri):
            return
        manager = XmlNamespaceManager()
        manager.add_namespace(RelationshipManager.namespace)
        stream = part_container.get_part(self.relationship_uri).stream
        root = cElementTree.fromstring(stream.read())
        for node in manager.select(root):
            _, tag = xml_tag_split(node.tag)
            if tag != RelationshipManager.XML_TAG_NAME:
                continue
            relationship_id = node.get(RelationshipManager.XML_ATTR_ID)
            relationship_type = node.get(RelationshipManager.XML_ATTR_TYPE)
            target_mode = node.get(RelationshipManager.XML_ATTR_TARGETMODE)
            target_uri = node.get(RelationshipManager.XML_ATTR_TARGET)
            self.create_relationship(
                target_uri=target_uri,
                target_mode=target_mode,
                relationship_type=relationship_type,
                relationship_id=relationship_id,
            )


class PackagePart(RelationshipManager):
    def __init__(self, uri, package):
        super(PackagePart, self).__init__()
        self.uri = uri
        self.package = package
        self.relationship_uri = PackagePart.get_relationship_part_uri(self.uri)

    @staticmethod
    def get_relationship_part_uri(part_uri):
        container, filename = path_split(part_uri)
        filename_rels = '%s.rels' % filename
        return zip_path_join(container, '_rels', filename_rels)

    @property
    def stream(self):
        raise NotImplementedError

    def get_part_container(self):
        return self.package


class PartContainer(object):
    def __init__(self):
        super(PartContainer, self).__init__()
        self._parts = None

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

    def create_part(self, uri):
        self.ensure_parts_are_loaded()
        if self.part_exists(uri):
            raise RuntimeError(
                'A part with the specified URI "%s" already exists' % (
                    uri,
                )
            )
        part = self.part_factory(
            package=self,
            uri=uri,
        )
        self.parts[uri] = part

    def part_exists(self, uri):
        return uri in self.parts

    def get_parts(self):
        return self.parts.values()

    def get_part(self, uri):
        return self.parts[uri]


class Package(RelationshipManager, PartContainer):
    part_factory = PackagePart

    def __init__(self):
        super(Package, self).__init__()
        self.uri = '/'
        self.relationship_uri = PackagePart.get_relationship_part_uri(self.uri)

    def get_part_container(self):
        return self


class ZipPackagePart(PackagePart):
    @property
    def stream(self):
        return self.package.streams[self.uri]


class ZipPackage(Package):
    part_factory = ZipPackagePart

    def __init__(self, path):
        super(ZipPackage, self).__init__()
        self.path = path
        self.streams = {}

    def load_parts(self):
        try:
            f = zipfile.ZipFile(self.path)
        except zipfile.BadZipfile:
            raise MalformedDocxException()
        try:
            uris = f.namelist()
            for uri in uris:
                self.streams['/' + uri] = f.open(uri, 'r')
        finally:
            f.close()
        for uri in self.streams:
            # The file paths in the zip package do not start with /
            self.create_part(uri)
