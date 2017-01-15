# Copyright 2016-2017 Tal Liron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file contains code that has been copied and changed from the ARIA
# TOSCA project, and thus is a Derivative Work (1):
#
# http://incubator.apache.org/projects/ariatosca.html
# git://git.apache.org/incubator-ariatosca.git
#
# * We provide a copy of the License, which is identical to ours (4a).
# * We prominently note here that we changed the file (4b).
# * We retain this copyright notice from the original work (4c): 
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# * The original work did not contain a NOTICE file (4d). 

from __future__ import absolute_import # so we can import 'collections'

from .types import type_name, import_symbol
from collections import OrderedDict
from inspect import isclass

def dedup(values):
    """
    Removes duplicate items from a list. Note that it does not change the original list.
    
    :param values: list
    :type values: list
    :returns: de-duped list
    :rtype: list
    """
    
    return list(OrderedDict.fromkeys(values))

class StrictList(list):
    """
    A list that raises :class:`TypeError` exceptions when objects of the wrong type are inserted.
    
    :param items: initial list
    :type items: list
    :param value_class: type required for list values
    :type value_class: type
    :param wrapper_function: calls this optional function on all values before added to the list
    :type wrapper_function: function
    :param unwrapper_function: calls this optional function on all values when retrieved from the
                               list
    :type unwrapper_function: function
    """

    def __init__(self, items=None, value_class=None, wrapper_function=None, unwrapper_function=None):
        super(StrictList, self).__init__()
        if isinstance(items, StrictList):
            self.value_class = items.value_class
            self.wrapper_function = items.wrapper_function
            self.unwrapper_function = items.unwrapper_function
        if isinstance(value_class, basestring):
            value_class = import_symbol(value_class)
            if not isclass(value_class):
                raise ValueError(u'%s is not a type' % value_class)
        self.value_class = value_class
        self.wrapper_function = wrapper_function
        self.unwrapper_function = unwrapper_function
        if items:
            for item in items:
                self.append(item)

    def _wrap(self, value):
        if (self.value_class is not None) and (not isinstance(value, self.value_class)):
            raise TypeError(u'value must be a "%s": %s' % (type_name(self.value_class), repr(value)))
        if self.wrapper_function is not None:
            value = self.wrapper_function(value)
        return value

    def _unwrap(self, value):
        if self.unwrapper_function is not None:
            value = self.unwrapper_function(value)
        return value

    def __getitem__(self, index):
        value = super(StrictList, self).__getitem__(index)
        value = self._unwrap(value)
        return value

    def __setitem__(self, index, value):
        value = self._wrap(value)
        return super(StrictList, self).__setitem__(index, value)

    def __iadd__(self, values):
        values = [self._wrap(v) for v in values]
        return super(StrictList, self).__iadd__(values)

    def append(self, value):
        value = self._wrap(value)
        return super(StrictList, self).append(value)

    def extend(self, values):
        values = [self._wrap(v) for v in values]
        return super(StrictList, self).extend(values)

    def insert(self, index, value):
        value = self._wrap(value)
        return super(StrictList, self).insert(index, value)

class StrictDict(OrderedDict):
    """
    An ordered dict that raises :class:`TypeError` exceptions when keys or values of the wrong type
    are used.
    
    :param items: initial dict
    :type items: dict
    :param key_class: type required for dict keys
    :type key_class: type
    :param value_class: type required for dict values
    :type value_class: type
    :param wrapper_function: calls this optional function on all values before added to the list
    :type wrapper_function: function
    :param unwrapper_function: calls this optional function on all values when retrieved from the
                               list
    :type unwrapper_function: function
    """

    def __init__(self, items=None, key_class=None, value_class=None, wrapper_function=None,
                 unwrapper_function=None):
        super(StrictDict, self).__init__()
        if isinstance(items, StrictDict):
            self.key_class = items.key_class
            self.value_class = items.value_class
            self.wrapper_function = items.wrapper_function
            self.unwrapper_function = items.unwrapper_function
        if isinstance(key_class, basestring):
            key_class = import_symbol(key_class)
            if not isclass(key_class):
                raise ValueError(u'%s is not a type' % key_class)
        if isinstance(value_class, basestring):
            value_class = import_symbol(value_class)
            if not isclass(value_class):
                raise ValueError(u'%s is not a type' % value_class)
        self.key_class = key_class
        self.value_class = value_class
        self.wrapper_function = wrapper_function
        self.unwrapper_function = unwrapper_function
        if items:
            for k, v in items:
                self[k] = v

    def __getitem__(self, key):
        if (self.key_class is not None) and (not isinstance(key, self.key_class)):
            raise TypeError(u'key must be a "%s": %s' % (type_name(self.key_class), repr(key)))
        value = super(StrictDict, self).__getitem__(key)
        if self.unwrapper_function is not None:
            value = self.unwrapper_function(value)
        return value

    def __setitem__(self, key, value, **_):
        if (self.key_class is not None) and (not isinstance(key, self.key_class)):
            raise TypeError(u'key must be a "%s": %s' % (type_name(self.key_class), repr(key)))
        if (self.value_class is not None) and (not isinstance(value, self.value_class)):
            raise TypeError(u'value must be a "%s": %s' % (type_name(self.value_class), repr(value)))
        if self.wrapper_function is not None:
            value = self.wrapper_function(value)
        return super(StrictDict, self).__setitem__(key, value)
