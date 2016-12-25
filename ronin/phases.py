
from .commands import Command

class Phase(object):
    def __init__(self, command=None, description=None, inputs=None, inputs_from=None, output=None):
        if command and not isinstance(command, Command):
            raise AttributeError('not an instance of %s: %s' % (Command.__name__, command.__class__.__name__)) # @UndefinedVariable
        
        self.command = command
        self.description = description
        self.inputs = inputs or []
        self.inputs_from = inputs_from or []
        self.output = output
