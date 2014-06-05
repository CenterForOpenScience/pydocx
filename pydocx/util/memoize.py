from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from collections import Hashable


class MulitMemoize(object):
    '''
    Adapted from: https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    func_names = {
        'find_all': find_all,
        ...
    }
    '''
    def __init__(self, func_names):
        self.cache = dict((func_name, {}) for func_name in func_names)
        self.func_names = func_names

    def __call__(self, func_name, *args):
        if not isinstance(args, Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func_names[func_name](*args)
        if args in self.cache[func_name]:
            return self.cache[func_name][args]
        else:
            value = self.func_names[func_name](*args)
            self.cache[func_name][args] = value
            return value


class MulitMemoizeMixin(object):
    def __init__(self, *args, **kwargs):
        super(MulitMemoizeMixin, self).__init__(*args, **kwargs)
        self._memoization = None

    def memod_tree_op(self, func_name, *args):
        return self._memoization(func_name, *args)

    def populate_memoization(self, func_names):
        self._memoization = MulitMemoize(func_names)
