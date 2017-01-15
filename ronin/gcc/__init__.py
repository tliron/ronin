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

from ..executors import ExecutorWithArguments
from ..contexts import current_context
from ..projects import Project
from ..utils.strings import stringify, stringify_list, bool_stringify, interpolate_later, join_later
from ..utils.paths import join_path, join_path_later
from ..utils.platform import which, platform_command, platform_executable_extension, platform_shared_library_extension, platform_shared_library_prefix
import os

DEFAULT_GCC_COMMAND = 'gcc'
DEFAULT_CCACHE_PATH = '/usr/lib/ccache'

def configure_gcc(gcc_command=None,
                  ccache=None,
                  ccache_path=None):
    """
    Configures the current context's `gcc <https://gcc.gnu.org/>`__ support.
    
    :param gcc_command: ``gcc`` (or ``g++``, etc.) command; defaults to "gcc"
    :type gcc_command: string|function
    :param ccache: whether to use ccache; defaults to True
    :type ccache: boolean
    :param ccache_path: ccache path; defaults to "/usr/lib/ccache"
    :type ccache_path: string|function
    """
    
    with current_context(False) as ctx:
        ctx.gcc.gcc_command = gcc_command or DEFAULT_GCC_COMMAND
        ctx.gcc.ccache = ccache
        ctx.gcc.ccache_path = ccache_path or DEFAULT_CCACHE_PATH

def which_gcc(command, ccache, platform, exception=True):
    """
    A specialized version of :func:`ronin.utils.platform.which` for `gcc <https://gcc.gnu.org/>`__
    that supports cross-compiling and `ccache <https://ccache.samba.org/>`__.
    
    Behind the scenes uses :func:`gcc_platform_command`.
    
    :param command: ``gcc`` (or ``g++``, etc.) command
    :type command: string|function
    :param ccache: set to True to attempt to use ccache; if a ccache version is not found,
                   will silently try to use the standard gcc command
    :type ccache: boolean
    :param platform: target platform or project
    :type platform: string|function|:class:`ronin.projects.Project`
    :param exception: set to False in order to return None upon failure, instead of raising an
                      exception
    :type exception: boolean
    :returns: absolute path to command
    :rtype: string
    :raises WhichException: if ``exception`` is True and could not find command
    """
    
    ccache = bool_stringify(ccache)
    if platform:
        command = gcc_platform_command(command, platform)
    if ccache:
        with current_context() as ctx:
            ccache_path = stringify(ctx.get('gcc.ccache_path', DEFAULT_CCACHE_PATH))
        r = which(join_path(ccache_path, command), exception=False)
        if r is not None:
            return r
    return which(command, exception=exception)

def gcc_platform_command(command, platform):
    """
    Finds the `gcc <https://gcc.gnu.org/>`__ command name for a specific target platform. 
    
    Behind the scenes uses :func:`ronin.utils.platform.platform_command`.

    :param command: ``gcc`` (or ``g++``, etc.) command
    :type command: string|function
    :param platform: target platform or project
    :type platform: string|function|:class:`ronin.projects.Project`
    :returns: command
    :rtype: string
    """
    
    if isinstance(platform, Project):
        platform = platform.variant
    return platform_command(command, platform)

def gcc_platform_machine_bits(platform):
    """
    Bits for target platform.
    
    :param platform: target platform or project
    :type platform: string|function|:class:`ronin.projects.Project`
    :returns: '64' or '32'
    :rtype: string
    """
    
    if isinstance(platform, Project):
        platform = platform.variant
    platform = stringify(platform)
    if platform:
        if platform.endswith('64'):
            return '64'
        elif platform.endswith('32'):
            return '32'
    return None

class GccExecutor(ExecutorWithArguments):
    """
    Base class for `gcc <https://gcc.gnu.org/>`__ executors.
    
    For a summary of all options accepted see the `documentation <https://gcc.gnu.org/onlinedocs
    /gcc-6.3.0/gcc/Option-Summary.html#Option-Summary>`__.
    """
    
    def __init__(self, command=None, ccache=True, platform=None):
        """
        :param command: ``gcc`` (or ``g++``, etc.) command; defaults to the context's ``gcc.gcc_command``
        :type command: string|function
        :param ccache: whether to use ccache; defaults to True
        :type ccache: boolean
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """
        
        super(GccExecutor, self).__init__()
        if platform is not None:
            self.set_machine(lambda _: gcc_platform_machine_bits(platform))
        self.command = lambda ctx: which_gcc(ctx.fallback(command, 'gcc.gcc_command', DEFAULT_GCC_COMMAND),
                                             ctx.fallback(ccache, 'gcc.cache', True),
                                             platform)
        self.add_argument_unfiltered('$in')
        self.add_argument_unfiltered('-o', '$out')
        self._platform = platform

    def enable_threads(self):
        self.add_argument('-pthread') # both compiler flags and linker libraries

    # Compiler
    
    def compile_only(self):
        self.add_argument('-c')
    
    def add_include_path(self, *value):
        self.add_argument(interpolate_later('-I%s', join_path_later(*value)))

    def standard(self, value):
        self.add_argument(interpolate_later('-std=%s', value))

    def define(self, name, value=None):
        if value is None:
            self.add_argument(interpolate_later('-D%s', name))
        else:
            self.add_argument(interpolate_later('-D%s=%s', name, value))

    def enable_warning(self, value='all'):
        self.add_argument(interpolate_later('-W%s', value))

    def disable_warning(self, value):
        self.add_argument(interpolate_later('-Wno-%s', value))
    
    def set_machine(self, value):
        self.add_argument(interpolate_later('-m%s', value))

    def set_machine_tune(self, value):
        self.add_argument(interpolate_later('-mtune=%s', value))

    def set_machine_floating_point(self, value):
        self.add_argument(interpolate_later('-mfpmath=%s', value))

    def optimize(self, value):
        self.add_argument(interpolate_later('-O%s', value))

    def enable_debug(self):
        self.add_argument('-g')

    def pic(self, compact=False):
        self.add_argument('-fpic' if compact else '-fPIC')
    
    # Linker

    def add_input(self, value):
        if value.endswith('.so'):
            value = value[:-3]
        elif value.endswith('.dll'):
            value = value[:-4]
        the_dir, the_file = os.path.split(value)
        if the_file.startswith('lib'):
            the_file = the_file[3:]
        self.add_library_path(the_dir)
        self.add_library(the_file)

    def add_library_path(self, *value):
        self.add_argument(interpolate_later('-L%s', join_path_later(*value)))

    def add_library(self, value):
        self.add_argument(interpolate_later('-l%s', value))
    
    def use_linker(self, value):
        self.add_argument(interpolate_later('-fuse-ld=%s', value))

    def link_static_only(self):
        self.add_argument('-static')

    def add_linker_argument(self, name, value=None, xlinker=True):
        """
        Add a command line argument to the linker.
        
        For options accepted by ld see the `documentation <https://sourceware.org/binutils
        /docs-2.27/ld/Options.html>`__
        """
        
        if xlinker:
            if value is None:
                self.add_argument('-Xlinker', name)
            else:
                self.add_argument('-Xlinker', interpolate_later('%s=%s', name, value))
        else:
            if value is None:
                self.add_argument(interpolate_later('-Wl,%s', name))
            else:
                self.add_argument(interpolate_later('-Xl,%s,%s', name, value))
    
    def linker_rpath(self, value):
        """
        Add a directory to the runtime library search path.
        """
        
        self.add_linker_argument('-rpath', interpolate_later("'%s'", value))

    def linker_rpath_origin(self):
        self.linker_rpath('$ORIGIN')

    def linker_disable_new_dtags(self):
        self.add_linker_argument('--disable-new-dtags')
        
    def linker_export_all_symbols_dynamically(self):
        self.add_argument('-rdynamic')

    def linker_no_undefined_symbols(self):
        self.add_linker_argument('--no-undefined')

    def linker_no_undefined_symbols_in_libraries(self):
        self.add_linker_argument('--no-allow-shlib-undefined')
    
    def linker_no_symbol_table(self):
        self.add_argument('-s')

    def linker_undefine_symbols(self, *values):
        for value in values:
            self.add_argument('-u', value)

    def linker_exclude_symbols(self, *values):
        self.add_linker_argument('-exclude-symbols', join_later(values, ','))
        
    def create_shared_library(self):
        self.add_argument('-shared')
        if self._platform is not None:
            if isinstance(self._platform, Project):
                self.output_extension = lambda _: self._platform.shared_library_extension
                self.output_prefix = lambda _: self._platform.shared_library_prefix
            else:
                self.output_extension = lambda _: platform_shared_library_extension(self._platform)
                self.output_prefix = lambda _: platform_shared_library_prefix(self._platform)
        else:
            self.output_extension = 'so'
            self.output_prefix = 'lib'

    # Makefile
    
    def create_makefile(self):
        self._makefile('D') # does not imply "-E"

    def create_makefile_ignore_system(self):
        self._makefile('MD')
    
    def create_makefile_only(self):
        self._makefile('') # implies "-E"

    def set_makefile_path(self, value):
        self._makefile('F', value)

    def _makefile(self, value, arg=None):
        if arg is not None:
            self.add_argument(interpolate_later('-M%s', value), arg)
        else:
            self.add_argument(interpolate_later('-M%s', value))

class _GccWithMakefile(GccExecutor):
    """
    Base class for `gcc <https://gcc.gnu.org/>`__ executors that also create a deps makefile.
    """
    
    def __init__(self, command=None, ccache=True, platform=None):
        """
        :param command: ``gcc`` (or ``g++``, etc.) command; defaults to the context's ``gcc.gcc_command``
        :type command: string|function
        :param ccache: whether to use ccache; defaults to True
        :type ccache: boolean
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """
        
        super(_GccWithMakefile, self).__init__(command, ccache, platform)
        self.create_makefile_ignore_system()
        self.add_argument_unfiltered('-MF', '$out.d') # set_makefile_path
        self._deps_file = '$out.d'
        self._deps_type = 'gcc'

class GccBuild(_GccWithMakefile):
    """
    `gcc <https://gcc.gnu.org/>`__ executor combining compilation and linking.
    
    The phase inputs are ".c" source files. The phase output is an executable (the default), an
    ".so" or ".dll" shared library (call :meth:`GccExecutor.create_shared_library`), or a static
    library (".a").
    """
    
    def __init__(self, command=None, ccache=True, platform=None):
        """
        :param command: ``gcc`` (or ``g++``, etc.) command; defaults to the context's ``gcc.gcc_command``
        :type command: string|function
        :param ccache: whether to use ccache; defaults to True
        :type ccache: boolean
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """

        super(GccBuild, self).__init__(command, ccache, platform)
        self.command_types = ['gcc_compile', 'gcc_link']
        if platform is not None:
            if isinstance(self._platform, Project):
                self.output_extension = lambda _: self._platform.executable_extension
            else:
                self.output_extension = lambda _: platform_executable_extension(platform)
        self.hooks.append(_debug_hook)

class GccCompile(_GccWithMakefile):
    """
    `gcc <https://gcc.gnu.org/>`__ compile executor.
    
    The phase inputs are ".c" source files. The phase outputs are ".o" object files.
    """

    def __init__(self, command=None, ccache=True, platform=None):
        """
        :param command: ``gcc`` (or ``g++``, etc.) command; defaults to the context's ``gcc.gcc_command``
        :type command: string|function
        :param ccache: whether to use ccache; defaults to True
        :type ccache: boolean
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """

        super(GccCompile, self).__init__(command, ccache, platform)
        self.command_types = ['gcc_compile']
        self.output_type = 'object'
        self.output_extension = 'o'
        self.compile_only()
        self.hooks.append(_debug_hook)

class GccLink(GccExecutor):
    """
    `gcc <https://gcc.gnu.org/>`__ link executor.
    
    The phase inputs are ".o" object files. The phase output is an executable (the default), an
    ".so" or ".dll" shared library (call ``create_shared_library``), or a static library (".a").
    """

    def __init__(self, command=None, ccache=True, platform=None):
        """
        :param command: ``gcc`` (or ``g++``, etc.) command; defaults to the context's ``gcc.gcc_command``
        :type command: string|function
        :param ccache: whether to use ccache; defaults to True
        :type ccache: boolean
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """

        super(GccLink, self).__init__(command, ccache, platform)
        self.command_types = ['gcc_link']
        if platform is not None:
            if isinstance(self._platform, Project):
                self.output_extension = lambda _: self._platform.executable_extension
            else:
                self.output_extension = lambda _: platform_executable_extension(platform)

def _debug_hook(executor):
    with current_context() as ctx:
        if ctx.get('build.debug', False):
            executor.enable_debug()
            executor.optimize('g')
