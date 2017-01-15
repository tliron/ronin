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

from .utils.strings import stringify, join_later
from .utils.collections import StrictList
from StringIO import StringIO

class Executor(object):
    """
    Base class for executors.
    
    :ivar command: command
    :vartype command: function|string
    :ivar command_types: command types supported (used by extensions)
    :vartype command_types: [string]
    :ivar output_extension: when calculating outputs, change extension to this
    :vartype output_extension: function|string
    :ivar output_prefix: when calculating outputs, prefix this to filename
    :vartype output_prefix: function|string
    :ivar hooks: called when generating the Ninja file
    :vartype hooks: [function]
    """
    
    def __init__(self):
        self.command = None
        self.command_types = StrictList(value_class=basestring)
        self.output_extension = None
        self.output_prefix = None
        self.output_type = 'binary'
        self.hooks = StrictList(value_class='types.FunctionType')
        self._deps_file = None
        self._deps_type = None

    def write_command(self, f, argument_filter=None):
        for hook in self.hooks:
            hook(self)
        f.write(stringify(self.command))
    
    def command_as_str(self, argument_filter=None):
        f = StringIO()
        try:
            self.write_command(f, argument_filter)
            v = f.getvalue()
        finally:
            f.close()
        return v

    def add_input(self, value):
        pass

class ExecutorWithArguments(Executor):
    """
    Base class for executors with arguments.
    """

    def __init__(self):
        super(ExecutorWithArguments, self).__init__()
        self._arguments = []

    def write_command(self, f, argument_filter=None):
        super(ExecutorWithArguments, self).write_command(f, argument_filter)
        arguments = []
        for append, to_filter, argument in self._arguments:
            argument = stringify(argument)
            if to_filter and argument_filter:
                argument = argument_filter(argument)
            if append:
                if argument not in arguments:
                    arguments.append(argument)
            else:
                arguments.remove(argument)
        if arguments:
            f.write(' ')
            f.write(' '.join(arguments))

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
            value = join_later(value)
        self._arguments.append((append, to_filter, value))
