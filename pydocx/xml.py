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

    def select(self, element):
        namespaces = tuple(self.namespaces)
        for child in element:
            if child.tag.startswith(namespaces):
                yield child
