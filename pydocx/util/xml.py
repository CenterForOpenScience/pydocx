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


def find_first(el, tag):
    """
    Find the first occurrence of a tag beneath the current element.
    """
    search_path = './/' + tag
    # Due to a bug in python 2.6's ElementPath implementation, we have to
    # strictly pass in a string
    # https://mail.python.org/pipermail/python-bugs-list/2008-July/056209.html
    search_path = str(search_path)
    return el.find(search_path)


def find_all(el, tag):
    """
    Find all occurrences of a tag
    """
    search_path = './/' + tag
    # Due to a bug in python 2.6's ElementPath implementation, we have to
    # strictly pass in a string
    # https://mail.python.org/pipermail/python-bugs-list/2008-July/056209.html
    search_path = str(search_path)
    return el.findall(search_path)


def find_ancestor_with_tag(pre_processor, el, tag):
    """
    Find the first ancestor with that is a `tag`.
    """
    while pre_processor.parent(el) is not None:
        el = pre_processor.parent(el)
        if el.tag == tag:
            return el
    return None


def has_descendant_with_tag(el, tag):
    """
    Determine if there is a child ahead in the element tree.
    """
    # Get child. stop at first child.
    return True if find_first(el, tag) is not None else False


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


def get_list_style(numbering_root, num_id, ilvl):
    # This is needed on both the custom lxml parser and the pydocx parser. So
    # make it a function.
    ids = find_all(numbering_root, 'num')
    for _id in ids:
        if _id.attrib['numId'] != num_id:
            continue
        abstractid = _id.find('abstractNumId')
        abstractid = abstractid.attrib['val']
        style_information = find_all(
            numbering_root,
            'abstractNum',
        )
        for info in style_information:
            if info.attrib['abstractNumId'] == abstractid:
                for i in el_iter(info):
                    if (
                            'ilvl' in i.attrib and
                            i.attrib['ilvl'] != ilvl):
                        continue
                    if i.find('numFmt') is not None:
                        return i.find('numFmt').attrib['val']


def parse_xml_from_string(xml, remove_namespaces=False):
    if remove_namespaces:
        xml = xml_remove_namespaces(xml)
    return cElementTree.fromstring(xml)


def convert_dictionary_to_style_fragment(style):
    items = sorted(style.items())
    return ';'.join("%s:%s" % item for item in items)


def convert_dictionary_to_html_attributes(attributes):
    items = sorted(attributes.items())
    return ' '.join('%s="%s"' % item for item in items)


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
