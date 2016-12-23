
from ..libraries import Library
from ..contexts import current_context
from ..utils import stringify, which
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
        self._name = name
        self._pkg_config_path = pkg_config_path
        self._data = None

    def add_to_compile(self, command):
        self._parse()
        if 'include_dirs' in self._data:
            for path in self._data['include_dirs']:
                command.add_include_path(path)
        if 'define_macros' in self._data:
            for define in self._data['define_macros']:
                command.define_symbol(define)

    def add_to_link(self, command):
        self._parse()
        if 'library_dirs' in self._data:
            for path in self._data['library_dirs']:
                command.add_library_path(path)
        if 'libraries' in self._data:
            for library in self._data['libraries']:
                command.add_library(library)

    def _parse(self):
        if self._data is not None:
            return
        with current_context() as ctx:
            pkg_config_command = stringify(ctx.get('pkg_config_command'))
            if pkg_config_command is not None:
                os.environ['PKG_CONFIG'] = pkg_config_command
            pkg_config_path = stringify(self._pkg_config_path)
            if pkg_config_path is not None:
                os.environ['PKG_CONFIG_PATH'] = pkg_config_path
            else:
                pkg_config_path = stringify(ctx.get('pkg_config_path'))
                if pkg_config_path is not None:
                    os.environ['PKG_CONFIG_PATH'] = pkg_config_path
            self._data = pkgconfig.parse(self._name)
