
from .libraries import Libraries
from .utils.strings import stringify, join_stringify_lambda
from cStringIO import StringIO

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
        Libraries(self.libraries).add_to_command(self)
        super(CommandWithLibraries, self).write(io)
