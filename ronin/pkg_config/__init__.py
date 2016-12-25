
from ..contexts import current_context
from ..libraries import Library
from ..utils.strings import stringify, UNESCAPED_STRING_RE
from ..utils.platform import which
from subprocess import check_output
import os

DEFAULT_COMMAND = 'pkg-config'

def configure_pkg_config(command=None, path=None):
    with current_context(False) as ctx:
        ctx.pkg_config_command = command
        ctx.pkg_config_path = path

class Package(Library):
    """
    A library that is configured by the external `pkg-config <https://www.freedesktop.org/wiki
    /Software/pkg-config/>__ tool.
    """
    
    def __init__(self, name, command=None, path=None, static=None):
        super(Package, self).__init__()
        self.name = name
        self.command = command
        self.path = path
        self.static = static

    def add_to_command_compile(self, command):
        for value in self._parse('--cflags'):
            if value.startswith('-I'):
                command.add_include_path(value[2:])
            elif value.startswith('-D'):
                k, v = value[2:].split('=', 2)
                command.define_symbol(k, v)

    def add_to_command_link(self, command):
        flags = ['--libs']
        if self.static:
            flags.append('--static')
        for value in self._parse(*flags):
            if value.startswith('-L'):
                command.add_library_path(value[2:])
            elif value.startswith('-l'):
                command.add_library(value[2:])

    def _parse(self, *flags):
        with current_context() as ctx:
            default = os.environ.get('PKG_CONFIG', DEFAULT_COMMAND)
            pkg_config_command = which(ctx.fallback(self.command, 'pkg_config_command', default), True)
            pkg_config_path = stringify(ctx.fallback(self.path, 'pkg_config_path'))
            if pkg_config_path is not None:
                os.environ['PKG_CONFIG_PATH'] = pkg_config_path

        args = [pkg_config_command]
        for flag in flags:
            args.append(flag)
        args.append(self.name)
 
        try:
            output = check_output(args).strip()
            return UNESCAPED_STRING_RE.split(output)
        except:
            raise Exception('failed to run: %s' % ' '.join(args))
