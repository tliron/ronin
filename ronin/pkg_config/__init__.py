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
from subprocess import check_output
import os

DEFAULT_COMMAND = 'pkg-config'

def configure_pkg_config(command=None, path=None):
    with current_context(False) as ctx:
        ctx.pkg_config_command = command
        ctx.pkg_config_path = path

class Package(Extension):
    """
    A library that is configured by the external `pkg-config <https://www.freedesktop.org/wiki
    /Software/pkg-config/>`__ tool.
    """
    
    def __init__(self, name, command=None, path=None, static=None):
        super(Package, self).__init__()
        self.name = name
        self.command = command
        self.path = path
        self.static = static

    def add_to_executor_gcc_compile(self, executor):
        for value in self._parse('--cflags'):
            if value.startswith('-I'):
                executor.add_include_path(value[2:])
            elif value.startswith('-D'):
                value = value[2:] 
                if '=' in value: 
                    k, v = value.split('=', 2)
                    executor.define_symbol(k, v)
                else:
                    executor.define_symbol(value)

    def add_to_executor_gcc_link(self, executor):
        flags = ['--libs']
        if self.static:
            flags.append('--static')
        for value in self._parse(*flags):
            if value.startswith('-L'):
                executor.add_library_path(value[2:])
            elif value.startswith('-l'):
                executor.add_library(value[2:])

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
