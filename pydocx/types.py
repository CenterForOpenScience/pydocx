from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


class SimpleType(object):
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return self.__nonzero__()


class OnOff(SimpleType):
    '''
    http://www.schemacentral.com/sc/ooxml/t-w_ST_OnOff.html

    >>> bool(OnOff('true'))
    True
    >>> bool(OnOff('on'))
    True
    >>> bool(OnOff('1'))
    True
    >>> bool(OnOff(''))
    True
    >>> bool(OnOff(None))
    True
    >>> bool(OnOff('false'))
    False
    >>> bool(OnOff('off'))
    False
    >>> bool(OnOff('0'))
    False
    >>> bool(OnOff('none'))
    False
    '''
    ON_VALUES = ['true', 'on', '1']

    def __nonzero__(self):
        return not self.value or self.value in self.ON_VALUES


class Underline(SimpleType):
    '''
    http://www.schemacentral.com/sc/ooxml/t-w_ST_Underline.html

    >>> bool(Underline('none'))
    False
    >>> bool(Underline(''))
    False
    >>> bool(Underline('single'))
    True
    '''

    def __nonzero__(self):
        OFF_VALUES = ['none', '', None]
        return self.value not in OFF_VALUES
