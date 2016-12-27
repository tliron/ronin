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
from glob2 import glob as _glob
import os

def join_path(*segments):
    segments = stringify_list(segments)
    segments = [v for v in segments if v is not None]
    def fix(v):
        return v[1:] if v.startswith(os.sep) else v
    if len(segments) > 1:
        segments = [segments[0]] + [fix(v) for v in segments[1:]]
    return os.path.join(*segments)

def join_path_later(*segments):
    return lambda _: join_path(*segments)

def base_path(path):
    path = stringify(path)
    return os.path.dirname(os.path.realpath(path))

def input_path(path):
    with current_context() as ctx:
        return join_path(ctx.get('input_path'), path)

def glob(path):
    path = stringify(path)
    with current_context() as ctx:
        return _glob(join_path(ctx.get('input_path'), path))

def change_extension(path, new_extension):
    path = stringify(path)
    new_extension = stringify(new_extension)
    if new_extension is None:
        return path
    dot = path.rfind('.')
    if dot != -1:
        path = path[:dot]
    return '%s.%s' % (path, new_extension)
