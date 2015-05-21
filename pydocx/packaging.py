from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import posixpath
import zipfile
from collections import defaultdict
from io import BytesIO

from pydocx.exceptions import MalformedDocxException
from pydocx.util.xml import (
    parse_xml_from_string,
    xml_tag_split,
    XmlNamespaceManager,
)


class PackageRelationship(object):
    '''
    Represents an association between a source Package or PackagePart, and a
    target object which can be a PackagePart or external resource.

    See also: http://msdn.microsoft.com/en-us/library/system.io.packaging.packagerelationship.aspx  # noqa
    '''

    namespace = '/'.join([
        'http://schemas.openxmlformats.org',
        'package',
        '2006',
        'relationships',
    ])

    TARGET_MODE_INTERNAL = 'Internal'
    TARGET_MODE_EXTERNAL = 'External'

    XML_TAG_NAME = 'Relationship'
    XML_ATTR_ID = 'Id'
    XML_ATTR_TARGETMODE = 'TargetMode'
    XML_ATTR_TARGET = 'Target'
    XML_ATTR_TYPE = 'Type'

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


class PackageRelationshipManager(object):
    '''
    An internal class used by ZipPackage and ZipPackagePart to abstract the
    package and part-level relationship management.
    '''

    def __init__(self):
        super(PackageRelationshipManager, self).__init__()
        self._relationships = None
        self.relationships_by_type = defaultdict(list)

    @property
    def relationships(self):
        if self._relationships is None:
            self._relationships = {}
            self._load_relationships()
        return self._relationships

    def _ensure_relationships_are_loaded(self):
        return self.relationships

    def get_relationships_by_type(self, relationship_type):
        self._ensure_relationships_are_loaded()
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
        self._ensure_relationships_are_loaded()
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

    def _load_relationships(self):
        part_container = self.get_part_container()
        if not part_container.part_exists(self.relationship_uri):
            return
        manager = XmlNamespaceManager()
        manager.add_namespace(PackageRelationship.namespace)
        stream = part_container.get_part(self.relationship_uri).stream
        root = parse_xml_from_string(stream.read())
        for node in manager.iterate_children(root):
            _, tag = xml_tag_split(node.tag)
            if tag != PackageRelationship.XML_TAG_NAME:
                continue
            relationship_id = node.get(PackageRelationship.XML_ATTR_ID)
            relationship_type = node.get(PackageRelationship.XML_ATTR_TYPE)
            target_mode = node.get(PackageRelationship.XML_ATTR_TARGETMODE)
            target_uri = node.get(PackageRelationship.XML_ATTR_TARGET)
            self.create_relationship(
                target_uri=target_uri,
                target_mode=target_mode,
                relationship_type=relationship_type,
                relationship_id=relationship_id,
            )


class ZipPackagePart(PackageRelationshipManager):
    '''
    Represents a data part within a ZipPackage.

    See also: http://msdn.microsoft.com/en-us/library/system.io.packaging.zippackagepart.aspx  # noqa
    '''

    def __init__(self, uri, package):
        super(ZipPackagePart, self).__init__()
        self.uri = uri
        self.package = package
        self.relationship_uri = ZipPackagePart.get_relationship_part_uri(
            self.uri,
        )

    @staticmethod
    def get_relationship_part_uri(part_uri):
        container, filename = posixpath.split(part_uri)
        filename_rels = '{file}.rels'.format(file=filename)
        return posixpath.join(container, '_rels', filename_rels)

    def get_part_container(self):
        return self.package

    @property
    def stream(self):
        return self.package.streams[self.uri]


class ZipPackage(PackageRelationshipManager):
    '''
    Represents a container that can that can store multiple data objects using
    a ZIP archive as a data store.

    See also: http://msdn.microsoft.com/en-us/library/system.io.packaging.zippackage.aspx  # noqa
    '''

    def __init__(self, path):
        super(ZipPackage, self).__init__()
        self.path = path
        self.streams = {}
        self.uri = '/'
        self._parts = None
        self.relationship_uri = ZipPackagePart.get_relationship_part_uri(
            self.uri,
        )

    def _load_parts(self):
        if self.path is None:
            return
        try:
            f = zipfile.ZipFile(self.path)
        except zipfile.BadZipfile:
            raise MalformedDocxException()
        try:
            uris = f.namelist()
            for uri in uris:
                data = f.read(uri)
                self.streams[self.uri + uri] = BytesIO(data)
        finally:
            f.close()
        for uri in self.streams:
            self.create_part(uri)

    def get_part_container(self):
        return self

    @property
    def parts(self):
        if self._parts is None:
            self._parts = {}
            self._load_parts()
        return self._parts

    def _ensure_parts_are_loaded(self):
        return self.parts

    def create_part(self, uri):
        self._ensure_parts_are_loaded()
        if self.part_exists(uri):
            raise RuntimeError(
                'A part with the specified URI "{uri}" already exists'.format(
                    uri=uri,
                )
            )
        part = ZipPackagePart(package=self, uri=uri)
        self.parts[uri] = part
        return part

    def part_exists(self, uri):
        return uri in self.parts

    def get_parts(self):
        return self.parts.values()

    def get_part(self, uri, default=None):
        return self.parts.get(uri, default)
