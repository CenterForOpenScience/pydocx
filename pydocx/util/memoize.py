# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import collections
import functools


class memoized(object):
    '''
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.set_cache(value, *args)
            return value

    def set_cache(self, value, *args):
        self.cache[args] = value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        func = functools.partial(self.__call__, obj)
        setattr(func, 'memo', self)
        return func
