from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import re
from xml.etree import cElementTree
from xml.parsers.expat import ExpatError

try:
    from defusedxml.cElementTree import fromstring
    cElementTree.fromstring = fromstring
except ImportError:
    pass

from pydocx.exceptions import MalformedDocxException


def filter_children(element, tags):
    return [
        el for el in element.getchildren()
        if el.tag in tags
    ]


def el_iter(el):
    """
    Go through all elements
    """
    try:
        for child in el.iter():
            yield child
    except AttributeError:
        # iter isn't available in < python 2.7
        for child in el.getiterator():
            yield child


def xml_remove_namespaces(xml_bytes):
    """
    Given a stream of xml bytes, strip all namespaces from tag and attribute
    names.
    """
    try:
        root = parse_xml_from_string(xml_bytes, remove_namespaces=False)
    except (SyntaxError, ExpatError):
        raise MalformedDocxException('This document cannot be converted.')
    for child in el_iter(root):
        child.tag = child.tag.split("}")[-1]
        child.attrib = dict(
            (k.split("}")[-1], v)
            for k, v in child.attrib.items()
        )
    # Regardless of whatever the original encoding was
    # (fromstring deals with it for us), always deal in terms of utf-8
    # internally.
    return cElementTree.tostring(root, encoding='utf-8')


def parse_xml_from_string(xml, remove_namespaces=False):
    if remove_namespaces:
        xml = xml_remove_namespaces(xml)
    return cElementTree.fromstring(xml)


def convert_dictionary_to_style_fragment(style):
    items = sorted(style.items())
    return ';'.join("%s:%s" % item for item in items)


def convert_dictionary_to_html_attributes(attributes):
    return ' '.join(
        '{k}="{v}"'.format(k=k, v=v)
        for k, v in
        sorted(attributes.items())
    )


def xml_tag_split(tag):
    '''
    Given a xml node tag, return the namespace and the tag name. The namespace
    is optional and will be None if not present.
    '''
    m = re.match('({([^}]+)})?(.+)', tag)
    groups = m.groups()
    return groups[1], groups[2]


class XmlNamespaceManager(object):
    '''
    Provides an interface for iterating through elements within an XML tree
    that are within a given set of namespaces.

    See also: http://msdn.microsoft.com/en-us/library/system.xml.xmlnamespacemanager.aspx  # noqa
    '''

    def __init__(self):
        self.namespaces = []

    def add_namespace(self, uri):
        self.namespaces.append('{%s}' % uri)

    def iterate_children(self, element):
        '''
        Returns a generator that yields back children of the given element
        which are in the namespaces managed by this instance.

        This method is provided as a convenience and is not part of the MSDN
        implementation.
        '''
        namespaces = tuple(self.namespaces)
        for child in element:
            if child.tag.startswith(namespaces):
                yield child
