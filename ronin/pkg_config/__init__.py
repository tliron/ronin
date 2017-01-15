# Copyright 2016-2017 Tal Liron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ..contexts import current_context
from ..extensions import Extension
from ..utils.strings import stringify, UNESCAPED_STRING_RE
from ..utils.platform import which
from subprocess import check_output, CalledProcessError
import os

DEFAULT_PKG_CONFIG_COMMAND = 'pkg-config'

def configure_pkg_config(pkg_config_command=None,
                         pkg_config_path=None):
    """
    Configures the current context's `pkg-config <https://www.freedesktop.org/wiki/Software
    /pkg-config/>`__ support.
    
    :param pkg_config_command: ``pkg-config`` command; defaults to "pkg-config"
    :type pkg_config_command: string|function
    :param pkg_config_path: ``pkg-config`` path
    :type pkg_config_path: string|function
    """
    
    with current_context(False) as ctx:
        ctx.pkg_config.pkg_config_command = pkg_config_command or DEFAULT_PKG_CONFIG_COMMAND
        ctx.pkg_config.path = pkg_config_path

class Package(Extension):
    """
    A library that is configured by the external `pkg-config <https://www.freedesktop.org/wiki
    /Software/pkg-config/>`__ tool.
    
    Supports gcc-like executors.
    """
    
    def __init__(self, name, command=None, path=None, static=False):
        """
        :param name: package name
        :type name: string|function
        :param command: ``pkg-config`` command; defaults to the context's ``pkg_config.pkg_config_command`` 
        :type command: string|function
        :param path: ``pkg-config`` path; defaults to the context's ``pkg_config.path``
        :type path: string|function
        :param static: set to True to use static library linking
        :type static: boolean
        """
        
        super(Package, self).__init__()
        self.name = name
        self.command = command
        self.path = path
        self.static = static

    def apply_to_executor_gcc_compile(self, executor):
        _add_cflags_to_executor(executor, self._parse('--cflags'))

    def apply_to_executor_gcc_link(self, executor):
        flags = ['--libs']
        if self.static:
            flags.append('--static')
        _add_libs_to_executor(executor, self._parse(*flags))

    def _parse(self, *flags):
        original_pkg_config_path = os.environ.get('PKG_CONFIG_PATH', None)
        try:
            with current_context() as ctx:
                default = os.environ.get('PKG_CONFIG', DEFAULT_PKG_CONFIG_COMMAND)
                pkg_config_command = which(ctx.fallback(self.command, 'pkg_config.pkg_config_command', default))
                pkg_config_path = stringify(ctx.fallback(self.path, 'pkg_config.path'))
                if pkg_config_path is not None:
                    os.environ['PKG_CONFIG_PATH'] = pkg_config_path
    
            args = [pkg_config_command]
            for flag in flags:
                args.append(flag)
            args.append(stringify(self.name))
     
            try:
                output = check_output(args).strip()
                return UNESCAPED_STRING_RE.split(output)
            except CalledProcessError:
                raise Exception(u"failed to run: '%s'" % ' '.join(args))
        finally:
            if original_pkg_config_path is not None:
                os.environ['PKG_CONFIG_PATH'] = original_pkg_config_path

def _add_cflags_to_executor(executor, args):
    for value in args:
        if value.startswith('-I'):
            executor.add_include_path(value[2:])
        elif value.startswith('-D'):
            value = value[2:] 
            if '=' in value: 
                k, v = value.split('=', 2)
                executor.define(k, v)
            else:
                executor.define(value)

def _add_libs_to_executor(executor, args):
    for value in args:
        if value.startswith('-L'):
            executor.add_library_path(value[2:])
        elif value.startswith('-l'):
            executor.add_library(value[2:])
