def uri_is_internal(uri):
    """
    >>> uri_is_internal('/word/media/image1.png')
    True
    >>> uri_is_internal('http://google/images/image.png')
    False
    """
    return uri.startswith('/')


def uri_is_external(uri):
    """
    >>> uri_is_external('/word/media/image1.png')
    False
    >>> uri_is_external('http://google/images/image.png')
    True
    """
    return not uri_is_internal(uri)
