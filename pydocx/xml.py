class XmlNamespaceManager(object):
    def __init__(self):
        self.namespaces = []

    def add_namespace(self, uri):
        self.namespaces.append('{%s}' % uri)

    def select(self, element):
        namespaces = tuple(self.namespaces)
        for child in element:
            if child.tag.startswith(namespaces):
                yield child
