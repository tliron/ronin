
from ..contexts import current_context
from ..libraries import Library
from ..utils.strings import stringify
from ..utils.platform import which
import os, pkgconfig

def configure_pkg_config(command=None, path=None):
    with current_context(False) as ctx:
        ctx.pkg_config_command = command
        ctx.pkg_config_path = path

class Package(Library):
    """
    A library that is configured by the external `pkg-config <https://www.freedesktop.org/wiki
    /Software/pkg-config/>__ tool.
    """
    
    def __init__(self, name, command=None, path=None):
        super(Package, self).__init__()
        self.name = name
        self.command = command
        self.path = path
        self._data = None

    def add_to_command_compile(self, command):
        self._parse()
        include_dirs = self._data.get('include_dirs')
        if include_dirs:
            for path in include_dirs:
                command.add_include_path(path)
        define_macros = self._data.get('define_macros')
        if define_macros:
            for define, value in define_macros:
                command.define_symbol(define, value)

    def add_to_command_link(self, command):
        self._parse()
        library_dirs = self._data.get('library_dirs')
        if library_dirs:
            for path in library_dirs:
                command.add_library_path(path)
        libraries = self._data.get('libraries')
        if libraries:
            for library in libraries:
                command.add_library(library)

    def _parse(self):
        if self._data is not None:
            return
        
        with current_context() as ctx:
            pkg_config_command = stringify(ctx.fallback(self.command, 'pkg_config_command'))
            if pkg_config_command is not None:
                pkg_config_command = which(pkg_config_command)
                os.environ['PKG_CONFIG'] = pkg_config_command
                
            pkg_config_path = stringify(ctx.fallback(self.path, 'pkg_config_path'))
            if pkg_config_path is not None:
                os.environ['PKG_CONFIG_PATH'] = pkg_config_path
            
        self._data = pkgconfig.parse(self.name)
