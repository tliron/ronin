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

from .collections import dedup
from ..contexts import current_context
import re

UNESCAPED_STRING_RE = re.compile(r'(?<!\\) ')

def stringify_list(values):
    return [stringify(v) for v in values]

def stringify(value):
    if value is None:
        return None
    elif hasattr(value, '__call__'):
        with current_context() as ctx:
            value = value(ctx)
        return stringify(value)
    else:
        return str(value)

def bool_stringify(value):
    if value is None:
        return False
    elif hasattr(value, '__call__'):
        with current_context() as ctx:
            value = value(ctx)
        return bool_stringify(value)
    else:
        if isinstance(value, bool):
            return value
        return str(value).lower() == 'true'

def stringify_unique(values):
    values = stringify_list(values)
    return dedup(values)

def join_stringify_lambda(values, separator=' '):
    return lambda _: separator.join(stringify_list(values))
