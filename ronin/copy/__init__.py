
from ..commands import CommandWithArguments
from ..contexts import current_context
from ..utils.platform import which

def configure_copy(ctx, command=None):
    with current_context(False) as ctx:
        ctx.cp_command = command

class Copy(CommandWithArguments):
    """
    Copy command.
    """
    
    def __init__(self, command=None):
        super(Copy, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'cp_command', 'cp'), True)
        self.add_argument('$in')
        self.add_argument('$out')
