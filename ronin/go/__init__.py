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
from ..projects import Project
from ..utils.platform import which, platform_executable_extension
from ..utils.paths import join_path, join_path_later
from ..utils.types import verify_type
from ..utils.collections import dedup
import os

DEFAULT_GO_COMMAND = 'go'

def configure_go(go_command=None):
    """
    Configures the current context's `Go <https://golang.org/>`__ support.
    
    :param go_command: ``go`` command; defaults to "go"
    :type go_command: string|function
    """
    
    with current_context(False) as ctx:
        ctx.go.go_command = go_command or DEFAULT_GO_COMMAND

class GoExecutor(ExecutorWithArguments):
    """
    Base class for `Go <https://golang.org/>`__ executors.
    """

    def __init__(self, command=None):
        """
        :param command: ``go`` command; defaults to the context's ``go.go_command``
        :type command: string|function
        """
        
        super(GoExecutor, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'go.go_command', DEFAULT_GO_COMMAND))
        self.command_types = ['go']
    
class GoCompile(GoExecutor):
    """
    `Go <https://golang.org/>`__ compile executor.
    
    The phase inputs are ".go" source files. The phase outputs are ".o" object files.
    """
    
    def __init__(self, command=None):
        """
        :param command: ``go`` command; defaults to the context's ``go.go_command``
        :type command: string|function
        """

        super(GoCompile, self).__init__(command)
        self.output_type = 'object'
        self.output_extension = 'o'
        self.add_argument('tool', 'compile')
        self.add_argument_unfiltered('-o', '$out')
        self.hooks.append(_in_hook)

    def add_import_path(self, *values):
        self.add_argument('-I', join_path_later(*values))

    def local_import_path(self, *values):
        self.add_argument('-D', join_path_later(*values))

    def expected_import_path(self, *values):
        self.add_argument('-p', join_path_later(*values))

    def create_packages(self):
        self.add_argument('-pack')
        self.output_extension = 'a'

    def assume_complete(self):
        self.add_argument('-complete')
    
    def enable_memory_sanitizier(self):
        self.add_argument('-msan')

    def enable_race_detector(self):
        self.add_argument('-race')

    def enable_large_model(self):
        self.add_argument('-largemodel')

    def disable_inlining(self):
        self.add_argument('-l')

    def disable_local_imports(self):
        self.add_argument('-nolocalimports')

    def disable_unsafe_imports(self):
        self.add_argument('-u')

    def disable_errors_limit(self):
        self.add_argument('-e')

    def disable_optimizations(self):
        self.add_argument('-N')

class GoLink(GoExecutor):
    """
    `Go <https://golang.org/>`__ link executor.
    
    The phase inputs are ".o" object files. The phase output is an executable (the default), an
    ".so" or ".dll" shared library, or a static library (".a").
    """
    
    def __init__(self, command=None, platform=None):
        """
        :param command: ``go`` command; defaults to the context's ``go.go_command``
        :type command: string|function
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """

        super(GoLink, self).__init__(command)
        if platform is not None:
            if isinstance(platform, Project):
                self.output_extension = lambda _: platform.executable_extension
            else:
                self.output_extension = lambda _: platform_executable_extension(platform)
        self.add_argument('tool', 'link')
        self.add_argument_unfiltered('-o', '$out')
        self.hooks.append(_debug_hook)
        self.hooks.append(_in_hook)

    def add_import_path(self, *values):
        self.add_argument('-L', join_path_later(*values))

    def build_mode(self, value):
        self.add_argument('-buildmode', value)

    def executable_format(self, value):
        self.add_argument('-H', value)

    def ar(self, value):
        self.add_argument('-extar', value)

    def linker(self, value):
        self.add_argument('-extld', value)

    def link_mode(self, value):
        self.add_argument('-linkmode', value)

    def enable_memory_sanitizier(self):
        self.add_argument('-msan')

    def enable_race_detector(self):
        self.add_argument('-race')

    def disable_dynamic_header(self):
        self.add_argument('-d')

    def disable_version_checks(self):
        self.add_argument('-f')

    def disable_data_checks(self):
        self.add_argument('-g')

    def disable_debug(self):
        self.add_argument('-s')

class GoPackage(Extension):
    """
    A `Go <https://golang.org/>`__ package generated by another phase.
    """
    
    def __init__(self, project, phase_name):
        """
        :param project: project
        :type project: :class:`ronin.projects.Project`
        :param phase_name: phase name in project
        :type phase_name: string|function
        """
        
        super(GoPackage, self).__init__()
        verify_type(project, Project)
        self._project = project
        self._phase_name = phase_name

    def apply_to_phase(self, phase):
        verify_type(phase.executor, GoExecutor)
        phase.rebuild_on_from.append(self._phase_name)

    def apply_to_executor_go(self, executor):
        for path in self._output_paths:
            executor.add_import_path(path)

    @property
    def _output_paths(self):
        with current_context() as ctx:
            project_outputs = ctx.get('current.project_outputs')
        if project_outputs is None:
            return []
        phase_outputs = project_outputs.get(self._project)
        if phase_outputs is None:
            return []
        phase_outputs = phase_outputs.get(self._phase_name) or []
        return dedup([v.path for v in phase_outputs])

def _debug_hook(executor):
    with current_context() as ctx:
        if not ctx.get('build.debug', False):
            executor.disable_debug()

def _in_hook(executor):
    # Must be last argument
    executor.add_argument_unfiltered('$in')
