
from .commands import Command
from .utils.types import verify_type

class Phase(object):
    def __init__(self, command=None, description=None, inputs=None, inputs_from=None, output=None):
        if command:
            verify_type(command, Command)
        self.command = command
        self.description = description
        self.inputs = inputs or []
        self.inputs_from = inputs_from or []
        self.output = output
