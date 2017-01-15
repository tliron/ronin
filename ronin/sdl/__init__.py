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
from ..pkg_config import _add_cflags_to_executor, _add_libs_to_executor
from ..utils.strings import stringify, bool_stringify, UNESCAPED_STRING_RE
from ..utils.platform import which
from subprocess import check_output, CalledProcessError

DEFAULT_SDL_CONFIG_COMMAND = 'sdl2-config'

def configure_sdl(config_command=None,
                  static=None,
                  prefix=None,
                  exec_prefix=None):
    """
    Configures the current context's `SDL <https://www.libsdl.org/>`__ support.
    
    :param config_command: config command; defaults to "sdl2-config"
    :type config_command: string|function
    :param static: whether to link statically; defaults to False
    :type static: boolean
    :param prefix: sdl-config prefix
    :type prefix: string|function
    :param exec_prefix: sdl-config exec-prefix
    :type exec_prefix: string|function
    """
    
    with current_context(False) as ctx:
        ctx.sdl.config_command = config_command or DEFAULT_SDL_CONFIG_COMMAND
        ctx.sdl.static = static
        ctx.sdl.prefix = prefix
        ctx.sdl.exec_prefix = exec_prefix

class SDL(Extension):
    """
    The `SDL <https://www.libsdl.org/>`__ library, configured using the sdl2-config tool that
    comes with SDL's development distribution. Supports gcc-like executors.
    
    Note that you may also use :class:`ronin.pkg_config.Package` to use SDL. However, this tool
    offers some special options you might need.
    """
    
    def __init__(self, command=None, static=None, prefix=None, exec_prefix=None):
        """
        :param command: ``sdl-config`` command; defaults to the context's ``sdl.config_command``
        :type command: string|function
        :param static: whether to link statically; defaults to the context's ``sdl.config_static``
        :type static: boolean
        :param prefix: sdl-config prefix; defaults to the context's ``sdl.prefix``
        :type prefix: string|function
        :param exec_prefix: sdl-config exec-prefix; defaults to the context's ``sdl.exec_prefix``
        :type exec_prefix: string|function
        """
        
        super(SDL, self).__init__()
        self.command = command
        self.static = static
        self.prefix = prefix
        self.exec_prefix = exec_prefix

    def apply_to_executor_gcc_compile(self, executor):
        _add_cflags_to_executor(executor, self._parse('--cflags'))

    def apply_to_executor_gcc_link(self, executor):
        with current_context() as ctx:
            sdl_config_static = bool_stringify(ctx.fallback(self.static, 'sdl.static', False))
        _add_libs_to_executor(executor, self._parse('--static-libs' if sdl_config_static else '--libs'))

    def _parse(self, flags):
        with current_context() as ctx:
            sdl_config_command = which(ctx.fallback(self.command, 'sdl.config_command', DEFAULT_SDL_CONFIG_COMMAND))
            sdl_config_prefix = stringify(ctx.fallback(self.prefix, 'sdl.prefix'))
            sdl_config_exec_prefix = stringify(ctx.fallback(self.exec_prefix, 'sdl.exec_prefix'))
        
        args = [sdl_config_command, flags]
        if sdl_config_prefix is not None:
            args.append(u'--prefix=%s' % sdl_config_prefix)
        if sdl_config_exec_prefix is not None:
            args.append(u'--exec-prefix=%s' % sdl_config_exec_prefix)
        
        try:
            output = check_output(args).strip()
            return UNESCAPED_STRING_RE.split(output)
        except CalledProcessError:
            raise Exception(u"failed to run: '%s'" % ' '.join(args))
