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

from ..commands import CommandWithLibraries
from ..contexts import current_context
from ..projects import Project
from ..utils.strings import stringify, stringify_unique, bool_stringify, join_stringify_lambda
from ..utils.paths import join_path
from ..utils.platform import which
from ..utils.types import verify_type
import os

DEFAULT_COMMAND = 'gcc'
DEFAULT_CCACHE_PATH = '/usr/lib/ccache'

CROSSCOMPILE_COMMAND_PREFIXES = {
    'linux64': 'x86_64-linux-gnu-',
    'linux32': 'x86_64-linux-gnu-', #'i686-linux-gnu-',
    'win64': 'x86_64-w64-mingw32-',
    'win32': 'i686-w64-mingw32-'}

def configure_gcc(command=None, ccache=None, ccache_path=None):
    with current_context(False) as ctx:
        ctx.gcc_command = command
        ctx.gcc_ccache = ccache
        ctx.gcc_ccache_path = ccache_path

def gcc_crosscompile_command(project, command=None):
    def closure(ctx, project, command):
        if command is None:
            command = DEFAULT_COMMAND
        command = stringify(command)
        variant = stringify(project.variant)
        return '%s%s' % (CROSSCOMPILE_COMMAND_PREFIXES.get(variant, ''), command)
    return lambda ctx: closure(ctx, project, command)

def gcc_crosscompile_executable_extension(project):
    def closure(ctx, project):
        variant = stringify(project.variant)
        if variant in ('win64', 'win32'):
            return 'exe'
        return None
    return lambda ctx: closure(ctx, project)

def gcc_crosscompile_shared_library_extension(project):
    def closure(ctx, project):
        variant = stringify(project.variant)
        if variant in ('win64', 'win32'):
            return 'dll'
        return 'so'
    return lambda ctx: closure(ctx, project)

class GccCommand(CommandWithLibraries):
    """
    Base class for `gcc <https://gcc.gnu.org/>`__ commands.
    """
    
    def __init__(self, command=None, ccache=True, crosscompile=None):
        super(GccCommand, self).__init__()
        self.linker_arguments = []
        self.deps = 'gcc'
        self.add_argument('$in')
        self.set_output('$out')
        self.crosscompile = crosscompile
        if crosscompile is not None:
            verify_type(crosscompile, Project)
            self.command = gcc_crosscompile_command(crosscompile, command)
            self.set_machine_bits(crosscompile)
        else:
            self.command = lambda ctx: _gcc_which(ctx.fallback(command, 'gcc_command', DEFAULT_COMMAND),
                                                  ctx.fallback(ccache, 'gcc_cache', True))

    def write(self, io):
        super(GccCommand, self).write(io)
        if self.linker_arguments:
            io.write(' -Wl,')
            io.write(','.join(stringify_unique(self.linker_arguments)))
    
    def set_output(self, value):
        self.add_argument('-o', value)
    
    # Compiler
    
    def compile_only(self):
        self.add_argument('-c')
    
    def add_include_path(self, *value):
        self.add_argument(lambda _: '-I%s' % join_path(*value))

    def standard(self, value):
        self.add_argument(lambda _: '-std=%s' % stringify(value))

    def define_symbol(self, name, value=None):
        if (value is None) or (value == ''):
            self.add_argument(lambda _: '-D%s' % stringify(name))
        else:
            self.add_argument(lambda _: '-D%s=%s' % (stringify(name), stringify(value)))

    def enable_warning(self, value='all'):
        self.add_argument(lambda _: '-W%s' % stringify(value))

    def disable_warning(self, value):
        self.add_argument(lambda _: '-Wno-%s' % stringify(value))
    
    def set_machine(self, value):
        self.add_argument(lambda _: '-m%s' % stringify(value))

    def set_machine_bits(self, project):
        verify_type(project, Project)
        self.set_machine(lambda _: '32' if stringify(project.variant).endswith('32') else '64')

    def set_machine_tune(self, value):
        self.add_argument(lambda _: '-mtune=%s' % stringify(value))

    def set_machine_floating_point(self, value):
        self.add_argument(lambda _: '-mfpmath=%s' % stringify(value))

    def optimize(self, value):
        self.add_argument(lambda _: '-O%s' % stringify(value))

    def enable_debug(self):
        self.add_argument('-g')

    def enable_threads(self):
        self.add_argument('-pthreads')
    
    # Linker

    def add_library_path(self, *value):
        self.add_argument(lambda _: '-L%s' % join_path(*value))

    def add_library(self, value):
        self.add_argument(lambda _: '-l%s' % stringify(value))
    
    def add_result_library(self, value):
        if value.endswith('.so'):
            value = value[:-3]
            dir, file = os.path.split(value)
            if file.startswith('lib'):
                file = file[3:]
                self.add_library_path(dir)
                self.add_library(file)

    def add_linker_argument(self, value):
        self.linker_arguments.append(value)
    
    def link_dynamic(self):
        self.add_argument('-rdynamic')

    def undefine(self, value):
        self.add_argument('-u', value)
        
    def pic(self):
        self.add_argument('-fPIC')

    def create_shared_library(self):
        self.add_argument('-shared')
        self.pic()
        if self.crosscompile is not None:
            self.output_extension = gcc_crosscompile_shared_library_extension(self.crosscompile)
        else:
            self.output_extension = 'so'

    def create_static_library(self):
        self.add_argument('-static')
        self.output_extension = 'a'

    def use_ld(self, value):
        self.add_argument(lambda _: '-fuse-ld=%s' % stringify(value))

    def rpath(self, value):
        self.add_linker_argument(lambda _: "-rpath,'%s'" % stringify(value))

    def rpath_origin(self):
        self.rpath('$$ORIGIN')

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
        args = [lambda _: '-M%s' % stringify(value)]
        if arg is not None:
            args.append(arg)
        self.add_argument(*args)

class GccWithMakefile(GccCommand):
    """
    Base class for gcc commands that also create a makefile.
    """
    
    def __init__(self, command=None, ccache=True, crosscompile=None):
        super(GccWithMakefile, self).__init__(command, ccache, crosscompile)
        self.depfile = True
        self.create_makefile_ignore_system()
        self.set_makefile_path('$out.d')

class GccBuild(GccWithMakefile):
    """
    gcc command supporting both compilation and linking phases.
    """
    
    def __init__(self, command=None, ccache=True, crosscompile=None):
        super(GccBuild, self).__init__(command, ccache, crosscompile)
        self.command_types = ['gcc_compile', 'gcc_link']
        if crosscompile is not None:
            self.output_extension = gcc_crosscompile_executable_extension(crosscompile)
        with current_context() as ctx:
            if ctx.get('debug', False):
                self.enable_debug()

class GccCompile(GccWithMakefile):
    """
    gcc command supporting compilation phase only.
    """

    def __init__(self, command=None, ccache=True, crosscompile=None):
        super(GccCompile, self).__init__(command, ccache, crosscompile)
        self.command_types = ['gcc_compile']
        self.output_type = 'object'
        self.output_extension = 'o'
        self.compile_only()
        with current_context() as ctx:
            if ctx.get('debug', False):
                self.enable_debug()

class GccLink(GccCommand):
    """
    gcc command supporting linking phase only.
    """

    def __init__(self, command=None, ccache=True, crosscompile=None):
        super(GccLink, self).__init__(command, ccache, crosscompile)
        self.command_types = ['gcc_link']

def _gcc_which(command, ccache):
    command = stringify(command)
    ccache = bool_stringify(ccache)
    if ccache:
        with current_context() as ctx:
            ccache_path = stringify(ctx.get('gcc_ccache_path', DEFAULT_CCACHE_PATH))
        r = which(join_path(ccache_path, command))
        if r is not None:
            return r
    return which(command, True)
