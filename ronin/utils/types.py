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

from inspect import isclass

def import_symbol(name):
    """
    Imports a symbol based on its fully qualified name.
    
    :param name: symbol name
    :type name: string
    :returns: symbol
    :raises ImportError: if could not import the module
    :raises AttributeError: if could not find the symbol in the module
    """
    
    if name and ('.' in name):
        module_name, name = name.rsplit('.', 1)
        return getattr(__import__(module_name, fromlist=[name], level=0), name)
    raise ImportError('import not found: %s' % name)

def type_name(the_type):
    """
    Human-readable name of type. Built-in types will avoid the "__builtin__" prefix.
    
    :param the_type: type
    :type the_type: type
    :returns: name of type
    :rtype: string
    """
    
    module = unicode(the_type.__module__)
    name = unicode(the_type.__name__)
    return name if module == '__builtin__' else u'%s.%s' % (module, name)

def verify_type(value, the_type):
    """
    Raises :class:`TypeError` if the value is not an instance of the type.

    :param value: value
    :param the_type: type or type name
    :type the_type: type|string
    :raises TypeError: if ``value`` is not an instance of ``the_type``
    :raises ValueError: if ``the_type`` is invalid
    :raises ImportError: if could not import the module
    :raises AttributeError: if could not find the symbol in the module
    """
    
    if isinstance(the_type, basestring):
        the_type = import_symbol(the_type)
        if not isclass(the_type):
            raise ValueError(u'%s is not a type' % the_type)
    
    if not isinstance(value, the_type):
        raise TypeError(u'not an instance of %s: %s' % (type_name(the_type), type_name(type(value)))) 

def verify_subclass(value, the_type):
    """
    Raises :class:`TypeError` if the value is not a subclass of the type.

    :param value: value
    :param the_type: type or type name
    :type the_type: type|string
    :raises TypeError: if ``value`` is not a subclass of ``the_type``
    :raises ValueError: if ``the_type`` is invalid
    :raises ImportError: if could not import the module
    :raises AttributeError: if could not find the symbol in the module
    """

    if isinstance(the_type, basestring):
        the_type = import_symbol(the_type)
        if not isclass(the_type):
            raise ValueError(u'%s is not a type' % the_type)
    
    if not issubclass(value, the_type):
        raise TypeError(u'not a subclass of %s: %s' % (type_name(the_type), type_name(type(value))))

def verify_type_or_subclass(value, the_type):
    """
    Raises :class:`TypeError` if the value is not an instance or subclass of the type.

    :param value: value
    :param the_type: type or type name
    :type the_type: type|string
    :raises TypeError: if ``value`` is not an instance or subclass of ``the_type``
    :raises ValueError: if ``the_type`` is invalid
    :raises ImportError: if could not import the module
    :raises AttributeError: if could not find the symbol in the module
    """

    if isclass(value):
        verify_subclass(value, the_type)
    else:
        verify_type(value, the_type)
