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

from .contexts import current_context
from .utils.types import verify_type

class Extension(object):
    """
    Base class for extensions.
    """
    
    def __init__(self):
        self.extensions = []

    def apply_to_phase(self, phase):
        pass
    
    def apply_to_executor(self, executor):
        for command_type in executor.command_types:
            fn = getattr(self, 'apply_to_executor_%s' % command_type, None)
            if fn:
                fn(executor)

class ExplicitExtension(Extension):
    """
    An extension with explicitly stated data.
    """
    
    def __init__(self, inputs=[], include_paths=None, defines=None, library_paths=None, libraries=None):
        super(ExplicitExtension, self).__init__()
        self.inputs = inputs or []
        self.include_paths = include_paths or []
        self.defines = defines or []
        self.library_paths = library_paths or []
        self.libraries = libraries or []

    def apply_to_phase(self, phase):
        phase.inputs += self.inputs

    def apply_to_executor_gcc_compile(self, executor):
        for path in self.include_paths:
            executor.add_include_path(path)
        for define, value in self.defines:
            executor.define(define, value)

    def apply_to_executor_gcc_link(self, executor):
        for path in self.library_paths:
            executor.add_library_path(path)
        for library in self.libraries:
            executor.add_library(library)

class ResultsExtension(Extension):
    """
    An extension that adds results from another build phase.
    """
    
    def __init__(self, phase):
        super(ResultsExtension, self).__init__()
        from .phases import Phase 
        verify_type(phase, Phase)
        self._phase = phase
    
    def apply_to_executor_gcc_link(self, executor):
        with current_context() as ctx:
            results = ctx.get('_phase_results')
        if results is None:
            return
        results = results.get(self._phase)
        if results is None:
            return
        for result in results:
            executor.add_result(result)
