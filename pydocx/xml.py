from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


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
