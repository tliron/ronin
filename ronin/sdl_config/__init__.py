
from ..contexts import current_context
from ..libraries import Library
from ..utils.strings import stringify, bool_stringify, UNESCAPED_STRING_RE
from ..utils.platform import which
from subprocess import check_output

DEFAULT_COMMAND = 'sdl2-config'

def configure_sdl_config(command=None, static=None, prefix=None, exec_prefix=None):
    with current_context(False) as ctx:
        ctx.sdl_config_command = command
        ctx.sdl_config_static = static
        ctx.sdl_config_prefix = prefix
        ctx.sdl_config_exec_prefix = exec_prefix

class SDL(Library):
    def __init__(self, command=None, static=None, prefix=None, exec_prefix=None):
        super(SDL, self).__init__()
        self.command = command
        self.static = static
        self.prefix = prefix
        self.exec_prefix = exec_prefix

    def add_to_command_compile(self, command):
        for flag in self._parse('--cflags'):
            command.add_argument(flag)

    def add_to_command_link(self, command):
        with current_context() as ctx:
            sdl_config_static = bool_stringify(ctx.fallback(self.static, 'sdl_config_static', False))
        for flag in self._parse('--static-libs' if sdl_config_static else '--libs'):
            command.add_argument(flag)

    def _parse(self, flags):
        with current_context() as ctx:
            sdl_config_command = which(ctx.fallback(self.command, 'sdl_config_command', DEFAULT_COMMAND))
            sdl_config_prefix = stringify(ctx.fallback(self.prefix, 'sdl_config_prefix'))
            sdl_config_exec_prefix = stringify(ctx.fallback(self.exec_prefix, 'sdl_config_exec_prefix'))
        args = [sdl_config_command, flags]
        if sdl_config_prefix is not None:
            args.append('--prefix=%s' % sdl_config_prefix)
        if sdl_config_exec_prefix is not None:
            args.append('--exec-prefix=%s' % sdl_config_exec_prefix)
        return UNESCAPED_STRING_RE.split(check_output(args).strip())
