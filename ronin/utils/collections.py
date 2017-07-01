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
    A list that raises :class:`~exceptions.TypeError` exceptions when objects of the wrong type are
    inserted.
    
    :param items: initial list
    :type items: list
    :param value_type: type(s) required for list values
    :type value_type: :obj:`type` or :obj:`basestring` or (:obj:`type` or :obj:`basestring`)
    :param wrapper_function: calls this optional function on all values before added to the list
    :type wrapper_function: ~types.FunctionType
    :param unwrapper_function: calls this optional function on all values when retrieved from the
     list
    :type unwrapper_function: ~types.FunctionType
    """

    def __init__(self, items=None, value_type=None, wrapper_function=None, unwrapper_function=None):
        super(StrictList, self).__init__()
        if isinstance(items, StrictList):
            self.value_type = items.value_type
            self.wrapper_function = items.wrapper_function
            self.unwrapper_function = items.unwrapper_function
        self.value_type = _convert_type(value_type)
        self.wrapper_function = wrapper_function
        self.unwrapper_function = unwrapper_function
        if items:
            for item in items:
                self.append(item)

    def _wrap(self, value):
        if (self.value_type is not None) and (not isinstance(value, self.value_type)):
            raise TypeError(u'value must be a "{}": {!r}'.format(type_name(self.value_type), value))
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
    An ordered dict that raises :class:`~exceptions.TypeError` exceptions when keys or values of the
    wrong type are used.
    
    :param items: initial dict
    :type items: dict
    :param key_type: type(s) required for dict keys
    :type key_type: :obj:`type` or :obj:`basestring` or (:obj:`type` or :obj:`basestring`)
    :param value_type: type(s) required for dict values
    :type value_type: :obj:`type` or :obj:`basestring` or (:obj:`type` or :obj:`basestring`)
    :param wrapper_function: calls this optional function on all values before added to the list
    :type wrapper_function: ~types.FunctionType
    :param unwrapper_function: calls this optional function on all values when retrieved from the
     list
    :type unwrapper_function: ~types.FunctionType
    """

    def __init__(self, items=None, key_type=None, value_type=None, wrapper_function=None,
                 unwrapper_function=None):
        super(StrictDict, self).__init__()
        if isinstance(items, StrictDict):
            self.key_type = items.key_type
            self.value_type = items.value_type
            self.wrapper_function = items.wrapper_function
            self.unwrapper_function = items.unwrapper_function
        self.key_type = _convert_type(key_type)
        self.value_type = _convert_type(value_type)
        self.wrapper_function = wrapper_function
        self.unwrapper_function = unwrapper_function
        if items:
            for k, v in items:
                self[k] = v

    def __getitem__(self, key):
        if (self.key_type is not None) and (not isinstance(key, self.key_type)):
            raise TypeError(u'key must be a "{}": {!r}'.format(type_name(self.key_type), key))
        value = super(StrictDict, self).__getitem__(key)
        if self.unwrapper_function is not None:
            value = self.unwrapper_function(value)
        return value

    def __setitem__(self, key, value, **_):
        if (self.key_type is not None) and (not isinstance(key, self.key_type)):
            raise TypeError(u'key must be a "{}": {!r}'.format(type_name(self.key_type), key))
        if (self.value_type is not None) and (not isinstance(value, self.value_type)):
            raise TypeError(u'value must be a "{}": {!r}'.format(type_name(self.value_type), value))
        if self.wrapper_function is not None:
            value = self.wrapper_function(value)
        return super(StrictDict, self).__setitem__(key, value)


def _convert_type(the_type):
    if isinstance(the_type, tuple):
        return tuple(_convert_type(v) for v in the_type)
    elif isinstance(the_type, basestring):
        the_type = import_symbol(the_type)
    if not isclass(the_type):
        raise ValueError(u'{} is not a type'.format(the_type))
    return the_type
