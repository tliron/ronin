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

class SDL(Extension):
    """
    The `SDL <https://www.libsdl.org/>`__ library, configured using the `sdl2-config` tool that
    comes with SDL's development distribution.
    
    Note that you should also be able to use :code:`pkg-config` to configure SDL. However, this tool
    offers some special options you might need.
    """
    
    def __init__(self, command=None, static=None, prefix=None, exec_prefix=None):
        super(SDL, self).__init__()
        self.command = command
        self.static = static
        self.prefix = prefix
        self.exec_prefix = exec_prefix

    def add_to_executor_gcc_compile(self, executor):
        for flag in self._parse('--cflags'):
            executor.add_argument(flag)

    def add_to_executor_gcc_link(self, executor):
        with current_context() as ctx:
            sdl_config_static = bool_stringify(ctx.fallback(self.static, 'sdl_config_static', False))
        for flag in self._parse('--static-libs' if sdl_config_static else '--libs'):
            executor.add_argument(flag)

    def _parse(self, flags):
        with current_context() as ctx:
            sdl_config_command = which(ctx.fallback(self.command, 'sdl_config_command', DEFAULT_COMMAND), True)
            sdl_config_prefix = stringify(ctx.fallback(self.prefix, 'sdl_config_prefix'))
            sdl_config_exec_prefix = stringify(ctx.fallback(self.exec_prefix, 'sdl_config_exec_prefix'))
        
        args = [sdl_config_command, flags]
        if sdl_config_prefix is not None:
            args.append('--prefix=%s' % sdl_config_prefix)
        if sdl_config_exec_prefix is not None:
            args.append('--exec-prefix=%s' % sdl_config_exec_prefix)
        
        try:
            output = check_output(args).strip()
            return UNESCAPED_STRING_RE.split(output)
        except:
            raise Exception('failed to run: %s' % ' '.join(args))
