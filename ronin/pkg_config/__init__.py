
from ..libraries import Library
from ..contexts import current_context
from ..utils.strings import stringify
from ..utils.platform import which
import os, pkgconfig

def configure_pkg_config(ctx, command='pkg-config', path=None):
    ctx.pkg_config_command = which(command)
    ctx.pkg_config_path = path

class Package(Library):
    """
    A library that is configured by the external `pkg-config <https://www.freedesktop.org/wiki
    /Software/pkg-config/>__ tool.
    """
    
    def __init__(self, name, pkg_config_path=None):
        super(Package, self).__init__()
        self.name = name
        self.pkg_config_path = pkg_config_path
        self._data = None

    def add_to_command_compile(self, command):
        self._parse()
        include_dirs = self._data.get('include_dirs')
        if include_dirs:
            for path in include_dirs:
                command.add_include_path(path)
        define_macros = self._data.get('define_macros')
        if define_macros:
            for define in define_macros:
                command.define_symbol(define)

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
            pkg_config_command = stringify(ctx.get('pkg_config_command'))
            if pkg_config_command is not None:
                os.environ['PKG_CONFIG'] = pkg_config_command
            pkg_config_path = stringify(self.pkg_config_path)
            if pkg_config_path is None:
                pkg_config_path = stringify(ctx.get('pkg_config_path'))
            if pkg_config_path is not None:
                os.environ['PKG_CONFIG_PATH'] = pkg_config_path
            self._data = pkgconfig.parse(self.name)
