class NamespacedNumId(object):
    def __init__(self, num_id, num_tables, *args, **kwargs):
        self._num_id = num_id
        self._num_tables = num_tables

    def __unicode__(self, *args, **kwargs):
        return '%s:%d' % (
            self._num_id,
            self._num_tables,
        )

    def __repr__(self, *args, **kwargs):
        return self.__unicode__(*args, **kwargs)

    def __eq__(self, other):
        if other is None:
            return False
        return repr(self) == repr(other)

    def __ne__(self, other):
        if other is None:
            return False
        return repr(self) != repr(other)

    @property
    def num_id(self):
        return self._num_id
