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

from .strings import stringify, stringify_list
from ..contexts import current_context
from glob2 import glob as glob2
import os

def join_path(*segments):
    """
    Joins the path segments into a single path tring. No attempt is made to make it an absolute
    path, nor to check that it exists on the filesystem.
    
    Null segments are skipped. Also note that unlike ``os.path.join``, segments beginning with a
    path separator character will not cause the path to reset.

    :param segments: path segments; calls :func:`ronin.utils.strings.stringify` on each
    :type segments: list of string or function
    :returns: joined path
    :rtype: string
    """
    
    segments = stringify_list(segments)
    segments = [v for v in segments if v is not None]
    def fix(v):
        return v[1:] if v.startswith(os.sep) else v
    if len(segments) > 1:
        segments = [segments[0]] + [fix(v) for v in segments[1:]]
    return os.path.join(*segments)

def join_path_later(*segments):
    """
    Like :func:`join_path`, but deferred.

    :param segments: path segments; calls :func:`ronin.utils.strings.stringify` on each
    :type segments: list of string or function or None 
    :returns: function that calls :func:`join_path`
    :rtype: function
    """
    
    return lambda _: join_path(*segments)

def base_path(path):
    """
    Returns the real base path string of a file. 

    :param path: path; calls :func:`ronin.utils.strings.stringify` on it
    :type path: string|function
    :returns: base path of ``path``
    :rtype: string
    """
    
    path = stringify(path)
    return os.path.dirname(os.path.realpath(path))

def input_path(*segments):
    """
    Joins the path segments to the context's ``paths.input``.
    
    See :func:`join_path`.

    :param segments: path segments; calls :func:`ronin.utils.strings.stringify` on each
    :type segments: list of string or function 
    :returns: path joined to ``paths.input``
    :rtype: string
    """
    
    with current_context() as ctx:
        return join_path(ctx.get('paths.input'), *segments)

def glob(pattern, path=None, hidden=False, dirs=False):
    """
    Returns a list of real path strings matching the pattern. If ``path`` is not specified,
    the pattern is implicitly joined to the context's ``paths.input``.
    
    Use "?" to match a single character, "\*" to match zero or more characters, and "\*\*" to match
    zero or more path segments.
    
    Note that this implementation improves on Python's standard :func:`glob.glob` by supporting
    "\*\*" correctly.
    
    :param pattern: pattern; calls :func:`ronin.utils.strings.stringify` on it
    :type pattern: string|function
    :param path: join the pattern to this path (when None, defaults to the context's
                 ``paths.input``); calls :func:`ronin.utils.strings.stringify` on it
    :type path: string|function
    :param hidden: set to True to include hidden files
    :type hidden: boolean
    :param dirs: set to True to include directories
    :type dirs: boolean
    :returns: zero or more full paths to files (and optionally directories) matching the pattern
    :rtype: list of string
    """

    if path is None:
        with current_context() as ctx:
            path = ctx.get('paths.input')
    paths = glob2(join_path(path, pattern), include_hidden=hidden)
    if not dirs:
        paths = [v for v in paths if not os.path.isdir(v)]
    return paths

def change_extension(path, new_extension):
    """
    Changes the file extension to a new one.
    
    The extension is defined as the segment following the last "." in the path.
    
    :param path: path; calls :func:`ronin.utils.strings.stringify` on it
    :type path: string|function
    :param new_extension: the new extension (if None, will return the path unchanged); calls
                          :func:`ronin.utils.strings.stringify` on it
    :type new_extension: string|function
    :returns: path with new extension
    :rtype: string
    """
    
    path = stringify(path)
    new_extension = stringify(new_extension)
    if new_extension is None:
        return path
    dot = path.rfind('.')
    if dot != -1:
        path = path[:dot]
    return u'%s.%s' % (path, new_extension)
