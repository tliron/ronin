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
from ..extensions import Extension
from ..contexts import current_context
from ..phases import Phase
from ..ninja import pathify
from ..pkg_config import Package
from ..gcc import GccCompile
from ..utils.platform import which
from ..utils.paths import join_path_later
from ..utils.strings import format_later


DEFAULT_VALAC_COMMAND = 'valac'


def configure_vala(valac_command=None):
    """
    Configures the current context's `Vala <https://wiki.gnome.org/Projects/Vala>`__ support.
    
    :param valac_command: valac command; defaults to "valac"
    :type valac_command: basestring|FunctionType
    """
    
    with current_context(False) as ctx:
        ctx.vala.valac_command = valac_command or DEFAULT_VALAC_COMMAND


class ValaExecutor(ExecutorWithArguments):
    """
    Base class for `Vala <https://wiki.gnome.org/Projects/Vala>`__ executors.
    """
    
    def __init__(self, command=None):
        """
        :param command: ``valac`` command; defaults to the context's ``vala.valac_command``
        :type command: basestring|FunctionType
        """
        
        super(ValaExecutor, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'vala.valac_command',
                                                      DEFAULT_VALAC_COMMAND))
        self.add_argument_unfiltered('$in')

    def set_output_directory(self, *value):
        self.add_argument(format_later('--directory={}', join_path_later(*value)))
        
    def compile_only(self):
        self.add_argument('--compile')
    
    def create_c_code(self):
        self.add_argument('--ccode')
    
    def create_c_header(self, *value):
        self.add_argument(format_later('--header={}', join_path_later(*value)))

    def create_fast_vapi(self, *value):
        self.add_argument(format_later('--fast-vapi={}', join_path_later(*value)))
        
    def create_deps(self, *value):
        self.add_argument(format_later('--deps={}', join_path_later(*value)))
    
    def add_source_path(self, *value):
        self.add_argument(format_later('--basedir={}', join_path_later(*value)))
        
    def add_vapi_path(self, *value):
        self.add_argument(format_later('--vapidir={}', join_path_later(*value)))

    def add_gir_path(self, *value):
        self.add_argument(format_later('--girdir={}', join_path_later(*value)))
        
    def add_package(self, value):
        self.add_argument(format_later('--pkg={}', value))
    
    def enable_threads(self):
        self.add_argument('--thread')

    def enable_debug(self):
        self.add_argument('-g')
        
    def enable_experimental(self):
        self.add_argument('--enable-experimental')

    def enable_deprecated(self):
        self.add_argument('--enable-deprecated')
        
    def target_glib(self, value):
        self.add_argument(format_later('--target-glib={}', value))

    # cc

    def add_cc_argument(self, value):
        self.add_argument(format_later('--Xcc={}', value))

    def remove_cc_argument(self, value):
        self.remove_argument(format_later('--Xcc={}', value))

    def disable_cc_warnings(self):
        self.add_cc_argument('-w')

    def enable_cc_warnings(self):
        self.remove_cc_argument('-w')
      
 
class ValaBuild(ValaExecutor):
    """
    `Vala <https://wiki.gnome.org/Projects/Vala>`__ single-phase build executor. Behind the scenes
    the Vala source code is transpiled to C source code and fed into gcc.
    
    The phase inputs are ".vala" (or ".gs") source files. The single phase output is a binary.
    """
    
    def __init__(self, command=None):
        """
        :param command: ``valac`` command; defaults to the context's ``vala.valac_command``
        :type command: basestring|FunctionType
        """
        
        super(ValaBuild, self).__init__(command)
        self.command_types = ['vala', 'vala_build']
        self.add_argument_unfiltered('--output=$out')
        self.disable_cc_warnings() # valac creates C code riddled with warnings...
        self.hooks.append(_debug_hook)


class ValaApi(ValaExecutor):
    """
    `Vala <https://wiki.gnome.org/Projects/Vala>`__ executor that generates ".vapi" files. These
    files are useful for incremental compilation, because they are equivalent to the real source
    files for the purposes of imports, but are much faster for ``valac`` to process.

    The phase inputs are ".vala" (or ".gs") source files. The phase outputs are ".vapi" files.
    """
    
    def __init__(self, command=None):
        """
        :param command: ``valac`` command; defaults to the context's ``vala.valac_command``
        :type command: basestring|FunctionType
        """
        
        super(ValaApi, self).__init__(command)
        self.command_types = ['vala']
        self.output_type = 'source'
        self.output_extension = 'vapi'
        self.add_argument_unfiltered('--fast-vapi=$out')


class ValaTranspile(ValaExecutor):
    """
    `Vala <https://wiki.gnome.org/Projects/Vala>`__ executor that transpiles Vala source code to C
    source code.

    The phase inputs are ".vala" (or ".gs") source files. The phase outputs are ".c" source files.
    
    Due to the nature of the language, if the Vala source code import from other files, then they
    *must* be transpiled together, *or* a simplified ".vapi" version of these files can be used
    instead. For this reason, it's useful to precede transpilation with :class:`ValaApi` phases.
    Feed them into the ``apis`` arguments here.   
    """    
    
    def __init__(self, command=None, apis=None):
        """
        :param command: ``valac`` command; defaults to the context's ``vala.valac_command``
        :type command: basestring|FunctionType
        :param apis: phases with :class:`ValaApi` executors
        :type apis: [basestring|:class:`ronin.phases.Phase`]
        """
        
        super(ValaTranspile, self).__init__(command)
        self.apis = apis or []
        self.command_types = ['vala']
        self.output_type = 'source'
        self.output_extension = 'c'
        self.add_argument_unfiltered('--deps=$out.d')
        self._deps_file = '$out.d'
        self._deps_type = 'gcc'
        self.create_c_code()
        self.hooks.append(_transpile_hook)


class ValaGccCompile(GccCompile):
    """
    Identical to :class:`ronin.gcc.GccCompile`, just with a default configuration most suitable for
    compiling C code generated by :class:`ValaTranspile`. 
    """
    
    def __init__(self, command=None, ccache=True, platform=None):
        """
        :param command: ``gcc`` (or ``g++``, etc.) command; defaults to the context's
         ``gcc.gcc_command``
        :type command: basestring|FunctionType
        :param ccache: whether to use ccache; defaults to True
        :type ccache: bool
        :param platform: target platform or project
        :type platform: basestring|FunctionType|:class:`ronin.projects.Project`
        """

        super(ValaGccCompile, self).__init__(command, ccache, platform)
        self.standard('gnu89')
        self.disable_warning('incompatible-pointer-types')
        self.disable_warning('discarded-qualifiers')
        self.disable_warning('format-extra-args')


class ValaPackage(Extension):
    """
    A `Vala <https://wiki.gnome.org/Projects/Vala>`__ package.
    
    Internally may also have an extension usable by gcc executors, so it can be used with both Vala
    and gcc executors. 
    """
    
    def __init__(self, name=None, vapi_paths=None, c=True, c_compile_arguments=None, c_link_arguments=None):
        """
        :param name: package name
        :type name: basestring|FunctionType
        :param c: set to True (default) to automatically include a :class:`ronin.pkg_config.Package`
         of the same name (used by gcc-compatible phases), False to disable, or provide any
         arbitrary extension
        :type c: bool|:class:`ronin.extensions.Extension`
        :param c_compile_arguments: arguments to add to gcc-compatible compile executors
        :type c_compile_arguments: [basestring|FunctionType]
        :param c_link_arguments: arguments to add to gcc-compatible link executors
        :type c_link_arguments: [basestring|FunctionType]
        """
        
        super(ValaPackage, self).__init__()
        self.name = name
        if isinstance(c, Extension):
            self.extensions.append(c)
        elif c and name:
            self.extensions.append(Package(name))
        self.vapi_paths = vapi_paths or []
        self.c_compile_arguments = c_compile_arguments or []
        self.c_link_arguments = c_link_arguments or []
    
    def apply_to_executor_vala(self, executor):
        if self.name:
            executor.add_package(self.name)
        for path in self.vapi_paths:
            executor.add_vapi_path(path)

    def apply_to_executor_vala_build(self, executor):
        for arg in self.c_compile_arguments:
            executor.add_cc_argument(arg)
        for arg in self.c_link_arguments:
            executor.add_cc_argument(arg)

    def apply_to_executor_gcc_compile(self, executor):
        for arg in self.c_compile_arguments:
            executor.add_argument(arg)

    def apply_to_executor_gcc_link(self, executor):
        for arg in self.c_link_arguments:
            executor.add_argument(arg)


def _debug_hook(executor):
    with current_context() as ctx:
        if ctx.get('build.debug', False):
            executor.enable_debug()


def _transpile_hook(executor):
    # valac is so complicated:
    #
    # 1) '--output=' is not supported in '--ccode' mode, only a '--directory=' with '--basedir='.
    # 2) We need to have a '--use-fast-vapi=' argument for each .vapi produced by the API
    #    phase, *except* for the one produced for our input.
    #
    # See: https://wiki.gnome.org/Projects/Vala/Documentation/ParallelBuilds
    executor.add_argument_unfiltered('--basedir=$base_path')
    executor.add_argument_unfiltered('--directory=$output_path')
    executor.add_argument_unfiltered('$fast_vapis')

    with current_context() as ctx:
        phase = ctx.current.phase
    phase.rebuild_on_from += executor.apis
    phase.vars['base_path'] = _vala_base_path_var
    phase.vars['output_path'] = _vala_output_path_var
    phase.vars['fast_vapis'] = _vala_fast_vapis_var(executor.apis)


def _vala_base_path_var(output, inputs):
    with current_context() as ctx:
        return ctx.current.phase.input_path


def _vala_output_path_var(output, inputs):
    with current_context() as ctx:
        return ctx.current.phase.output_path


def _vala_fast_vapis_var(apis):
    def var(output, inputs):
        with current_context() as ctx:
            outputs = []
            for api in apis:
                if not isinstance(api, Phase):
                    api = ctx.current.project.phases[api]
                
                # All API inputs except ourselves
                api_inputs = [v for v in api.inputs if v not in inputs]
    
                # API outputs
                _, api_outputs = api.get_outputs(api_inputs)
                outputs += api_outputs
        
        return ' '.join([u'--use-fast-vapi={}'.format(pathify(v.file)) for v in outputs])
    return var
