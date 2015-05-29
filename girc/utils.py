#!/usr/bin/env python3
# Written by Daniel Oaks <daniel@danieloaks.net>
# Released under the ISC license
import collections


class NickMask:
    def __init__(self, mask):
        self.nick = ''
        self.user = ''
        self.host = ''

        if '!' in mask:
            self.nick, rest = mask.split('!', 1)
            if '@' in rest:
                self.user, self.host = rest.split('@', 1)
        else:
            self.nick = mask

    @property
    def userhost(self):
        return '{}@{}'.format(self.user, self.host)

    @property
    def nickmask(self):
        return '{}!{}@{}'.format(self.nick, self.user, self.host)


# just a custom casefolding list, designed for things like lists of keys
class CaseInsensitiveList(collections.MutableSequence):
    @staticmethod
    def _check_value(value):
        if not isinstance(value, object):
           raise TypeError()

    def __init__(self, data=None):
        self.__store = []

        if data:
            self.extend(data)

    def __getitem__(self, key):
        # try:except is here so iterating works properly
        try:
            return self.__store[key]
        except KeyError:
            raise IndexError

    def __setitem__(self, key, value):
        if isinstance(value, str):
            value = value.casefold()

        self._check_value(value)
        self.__store[key] = value

    def __delitem__(self, key):
        del self.__store[key]

    def __len__(self):
        return len(self.__store)

    def insert(self, key, value):
        if isinstance(value, str):
            value = value.casefold()

        self._check_value(value)
        self.__store.insert(key, value)

    def __contains__(self, value):
        if isinstance(value, str):
            value = value.casefold()

        return value in self.__store

    def __add__(self, other):
        self.extend(other)
        return self


# CaseInsensitiveDict from requests.
#
# Copyright 2015 Kenneth Reitz
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import time

class CaseInsensitiveDict(collections.MutableMapping):
    """
    A case-insensitive ``dict``-like object.
    Implements all methods and operations of
    ``collections.MutableMapping`` as well as dict's ``copy``. Also
    provides ``lower_items``.
    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive::
        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True
    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.
    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.casefold()``s, the
    behavior is undefined.
    """
    def __init__(self, data=None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.casefold()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.casefold()][1]

    def __delitem__(self, key):
        del self._store[key.casefold()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return (
            (lowerkey, keyval[1])
            for (lowerkey, keyval)
            in self._store.items()
        )

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))
