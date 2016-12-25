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

from .libraries import Library
from .utils.strings import stringify, join_stringify_lambda
from .utils.types import verify_type_or_subclass
from cStringIO import StringIO
from inspect import isclass

class Command(object):
    """
    Base class for commands.
    
    Commands represent rules for a Ninja file.
    """
    
    def __init__(self):
        self.command = None
        self.output_extension = None
        self.output_type = 'binary'
        self.depfile = False
        self.deps = None

    def write(self, io):
        io.write(stringify(self.command)) 

    def __str__(self):
        io = StringIO()
        try:
            self.write(io)
            v = io.getvalue()
        finally:
            io.close()
        return v

    def add_result_library(self, value):
        pass

class CommandWithArguments(Command):
    """
    Base class for commands with arguments.
    """

    def __init__(self):
        super(CommandWithArguments, self).__init__()
        self._arguments = []

    def write(self, io):
        super(CommandWithArguments, self).write(io)
        arguments = []
        for flag, argument in self._arguments:
            argument = stringify(argument)
            if flag:
                arguments.append(argument)
            else:
                arguments.remove(argument)
        if arguments:
            io.write(' ')
            io.write(' '.join(arguments))

    def add_argument(self, *value):
        self._argument(True, *value)

    def remove_argument(self, *value):
        self._argument(False, *value)

    def _argument(self, flag, *value):
        l = len(value)
        if l == 0:
            return
        elif l == 1:
            value = value[0]
        else:
            value = join_stringify_lambda(value)
        self._arguments.append((flag, value))

class CommandWithLibraries(CommandWithArguments):
    """
    Base class for commands with libraries.
    """

    def __init__(self):
        super(CommandWithLibraries, self).__init__()
        self.command_types = []
        self.libraries = []

    def write(self, io):
        for library in self.libraries:
            verify_type_or_subclass(library, Library)
            if isclass(library):
                library = library()
            library.add_to_command(self)
        
        super(CommandWithLibraries, self).write(io)
