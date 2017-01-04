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
from ..utils.paths import join_path, join_path_later
from ..utils.strings import interpolate_later

DEFAULT_VALAC_COMMAND = 'valac'

def configure_vala(command=None):
    with current_context(False) as ctx:
        ctx.vala.command = command or DEFAULT_VALAC_COMMAND

class _ValaExecutor(ExecutorWithArguments):
    """
    Base class for `Vala <https://wiki.gnome.org/Projects/Vala>`__ executors.
    """
    
    def __init__(self, command=None):
        super(_ValaExecutor, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'vala.command', DEFAULT_VALAC_COMMAND))
        self.add_argument_unfiltered('$in')

    def set_output_directory(self, *value):
        self.add_argument(interpolate_later('--directory=%s', join_path_later(*value)))
        
    def compile_only(self):
        self.add_argument('--compile')
    
    def create_c_code(self):
        self.add_argument('--ccode')
    
    def create_c_header(self, *value):
        self.add_argument(interpolate_later('--header=%s', join_path_later(*value)))

    def create_fast_vapi(self, *value):
        self.add_argument(interpolate_later('--fast-vapi=%s', join_path_later(*value)))
        
    def create_deps(self, *value):
        self.add_argument(interpolate_later('--deps=%s', join_path_later(*value)))
    
    def add_source_path(self, *value):
        self.add_argument(interpolate_later('--basedir=%s', join_path_later(*value)))
        
    def add_vapi_path(self, *value):
        self.add_argument(interpolate_later('--vapidir=%s', join_path_later(*value)))

    def add_gir_path(self, *value):
        self.add_argument(interpolate_later('--girdir=%s', join_path_later(*value)))
        
    def add_package(self, value):
        self.add_argument(interpolate_later('--pkg=%s', value))
    
    def enable_threads(self):
        self.add_argument('--thread')

    def enable_debug(self):
        self.add_argument('-g')
        
    def enable_experimental(self):
        self.add_argument('--enable-experimental')

    def enable_deprecated(self):
        self.add_argument('--enable-deprecated')
        
    def target_glib(self, value):
        self.add_argument(interpolate_later('--target-glib=%s', value))

    # cc

    def add_cc_argument(self, value):
        self.add_argument(interpolate_later('--Xcc=%s', value))

    def remove_cc_argument(self, value):
        self.remove_argument(interpolate_later('--Xcc=%s', value))

    def disable_cc_warnings(self):
        self.add_cc_argument('-w')

    def enable_cc_warnings(self):
        self.remove_cc_argument('-w')
        
class ValaBuild(_ValaExecutor):
    def __init__(self, command=None):
        super(ValaBuild, self).__init__(command)
        self.command_types = ['vala', 'vala_build']
        self.add_argument_unfiltered('--output=$out')
        self.disable_cc_warnings() # you pretty much always want this due to how valac creates C code
        self.hooks.append(_debug_hook)

class ValaApi(_ValaExecutor):
    def __init__(self, command=None):
        super(ValaApi, self).__init__(command)
        self.command_types = ['vala']
        self.output_type = 'source'
        self.output_extension = 'vapi'
        self.add_argument_unfiltered('--fast-vapi=$out')

class ValaTranspile(_ValaExecutor):
    def __init__(self, command=None, apis=None):
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
    def __init__(self, command=None, ccache=True, platform=None):
        super(ValaGccCompile, self).__init__(command, ccache, platform)
        self.standard('gnu89')
        self.disable_warning('incompatible-pointer-types')
        self.disable_warning('discarded-qualifiers')
        self.disable_warning('format-extra-args')

class ValaExtension(Extension):
    def __init__(self, name=None, package=True, vapi_paths=None, c_compile_arguments=None, c_link_arguments=None):
        super(ValaExtension, self).__init__()
        self.name = name
        if isinstance(package, Package):
            self.package = package
        elif package and name:
            self.package = Package(name)
        else:
            self.package = None
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
        if self.package:
            self.package.apply_to_executor_gcc_compile(executor)

    def apply_to_executor_gcc_link(self, executor):
        for arg in self.c_link_arguments:
            executor.add_argument(arg)
        if self.package:
            self.package.apply_to_executor_gcc_link(executor)

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
        return ctx.paths.root
        
def _vala_output_path_var(output, inputs):
    with current_context() as ctx:
        return ctx.current.phase.get_output_path(ctx.current.output_path)

def _vala_fast_vapis_var(apis):
    def var(output, inputs):
        outputs = []
        for api in apis:
            # All API inputs except ourselves
            api_inputs = [v for v in api.inputs if v not in inputs]

            # API outputs
            with current_context() as ctx:
                _, api_outputs = api.get_outputs(ctx.current.output_path, api_inputs)
            outputs += api_outputs
        
        return ' '.join(['--use-fast-vapi=%s' % pathify(v.file) for v in outputs])
    return var
