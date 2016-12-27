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

from .utils.strings import stringify, join_stringify_lambda
from cStringIO import StringIO

class Executor(object):
    """
    Base class for executors.
    """
    
    def __init__(self):
        self.command = None
        self.command_types = []
        self.output_extension = None
        self.output_prefix = None
        self.output_type = 'binary'
        self.hooks = []
        self._deps_file = None
        self._deps_type = None

    def write_command(self, io, filter=None):
        for hook in self.hooks:
            hook(self)
        io.write(stringify(self.command))
    
    def command_as_str(self, filter=None):
        io = StringIO()
        try:
            self.write_command(io, filter)
            v = io.getvalue()
        finally:
            io.close()
        return v

    def add_result(self, value):
        pass

class ExecutorWithArguments(Executor):
    """
    Base class for executors with arguments.
    """

    def __init__(self):
        super(ExecutorWithArguments, self).__init__()
        self._arguments = []

    def write_command(self, io, filter=None):
        super(ExecutorWithArguments, self).write_command(io, filter)
        arguments = []
        for append, to_filter, argument in self._arguments:
            argument = stringify(argument)
            if to_filter and filter:
                argument = filter(argument)
            if append:
                if argument not in arguments:
                    arguments.append(argument)
            else:
                arguments.remove(argument)
        if arguments:
            io.write(' ')
            io.write(' '.join(arguments))

    def add_argument(self, *value):
        self._argument(True, True, *value)

    def add_argument_unfiltered(self, *value):
        self._argument(True, False, *value)

    def remove_argument(self, *value):
        self._argument(False, True, *value)

    def remove_argument_unfiltered(self, *value):
        self._argument(False, False, *value)

    def _argument(self, append, to_filter, *value):
        l = len(value)
        if l == 0:
            return
        elif l == 1:
            value = value[0]
        else:
            value = join_stringify_lambda(value)
        self._arguments.append((append, to_filter, value))
