"""
Created on 4 Apr 2017

@author: jdrumgoole
"""


class NestedDict(dict):
    """
    NestedDict
    ===========
    A NestedDict is a dictionary in which nested objects can be accessed used
    a dotted key notation.
    Hence

    >>> a = NestedDict({"a":{"b":{"c":1}}})
    >>> a
    {'a': {'b': {'c': 1}}}
    >>> a['a.b.c']
    1
    >>> a['a.b.c']=2
    >>> a['a.b.c']
    2

    """

    def _key_split(self, key):
        """
        Split a key into its component parts

        >>> a = NestedDict()
        >>> a._key_split("a.b.c")
        ['a', 'b', 'c']
        >>> a._key_split(3)
        Traceback (most recent call last):
        ValueError: Expected a <str> type

        :param key: a key of the form "a.b.c.d"
        :return: ['a', 'b', 'c', 'd']
        """
        if isinstance(key, str):
            return key.split('.')
        else:
            raise ValueError("Expected a <str> type")

    def _has_nested(self, d, keys):
        if len(keys) > 1 and isinstance(d, dict):
            if dict.__contains__(d, keys[0]):
                return self._has_nested(d[keys[0]], keys[1:])
            else:
                return False
        else:
            return dict.__contains__(d, keys[0])

    def _get_nested(self, d, keys):
        if len(keys) > 1 and isinstance(d, dict):
            if dict(d).__contains__(keys[0]):
                return self._get_nested(d[keys[0]], keys[1:])
            else:
                raise KeyError(f"no such key:{keys[0]}")
        else:
            return dict.__getitem__(d, keys[0])

    def _set_nested(self, d, keys, value):
        if len(keys) > 1 and isinstance(d, dict):
            if dict(d).__contains__(keys[0]):
                return self._set_nested(d[keys[0]], keys[1:], value)
            else:
                dict.__setitem__(d, keys[0], {})
        else:
            dict.__setitem__(d, keys[0], value)

    def _del_nested(self, d, keys):
        if len(keys) > 1 and isinstance(d, dict):
            if dict(d).__contains__(keys[0]):
                return self._del_nested(d[keys[0]], keys[1:])
            else:
                dict.__delitem__(d, keys[0])
        else:
            dict.__delitem__(d, keys[0])

    def __contains__(self, key):
        return self._has_nested(self, key.split('.'))

    def __getitem__(self, item):
        return self._get_nested(self, item.split('.'))

    def __setitem__(self, key, value):
        self._set_nested(self, key.split('.'), value)

    def get(self, key, default_value=None):
        try:
            return self._get_nested(self, key.split('.'))
        except KeyError:
            return default_value

    def has_key(self, key):
        try:
            return self._get_nested(self, key.split('.'))
        except KeyError:
            return False

    def __delitem__(self, key):
        self._del_nested(self, key.split('.'))

    def pop(self, key, default_value=None):
        try:
            v = self._get_nested(self, key.split('.'))
            self._del_nested(self, key.split('.'))
        except KeyError:
            v = default_value

        return v

    def popitem(self, key):
        v = self._get_nested(self, key.split('.'))
        self._del_nested(self, key.split('.'))
        return key, v


if __name__ == "__main__":
    import doctest
    doctest.testmod()
