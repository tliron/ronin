
from .utils import stringify, stringify_unique, join_stringify_lambda
from cStringIO import StringIO

class Command(object):
    """
    Base class for commands.
    
    Commands represent rules for a Ninja file.
    """
    
    def __init__(self):
        self.command = None
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
        self._remove_arguments = []

    def write(self, io):
        super(CommandWithArguments, self).write(io)
        if self._arguments:
            arguments = stringify_unique(self._arguments)
            remove_arguments = stringify_unique(self._remove_arguments)
            arguments = [v for v in arguments if v not in remove_arguments]
            if arguments:
                io.write(' ')
                io.write(' '.join(arguments))

    def add_argument(self, *value):
        self._argument(self._arguments, *value)

    def remove_argument(self, *value):
        self._argument(self._remove_arguments, *value)

    def _argument(self, arguments, *value):
        l = len(value)
        if l == 0:
            return
        elif l == 1:
            value = value[0]
        else:
            value = join_stringify_lambda(value)
        arguments.append(value)
