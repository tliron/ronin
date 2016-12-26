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

def join_path(*values):
    values = stringify_list(values)
    def fix(v):
        return v[1:] if v.startswith(os.pathsep) else v
    values = [v for v in values if v is not None]
    return os.path.join(*values)

def base_path(value):
    value = stringify(value)
    return os.path.dirname(os.path.realpath(value))

def input_path(value):
    with current_context() as ctx:
        return join_path(ctx.get('input_path'), value)

def glob(value):
    value = stringify(value)
    with current_context() as ctx:
        return _glob(join_path(ctx.get('input_path'), value))

def change_extension(value, new_extension):
    value = stringify(value)
    new_extension = stringify(new_extension)
    if new_extension is None:
        return value
    dot = value.rfind('.')
    if dot != -1:
        value = value[:dot]
    return '%s.%s' % (value, new_extension)
