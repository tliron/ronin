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

from .executors import Executor
from .extensions import Extension
from .utils.types import verify_type, verify_type_or_subclass
from inspect import isclass

class Phase(object):
    """
    A build phase.
    """
    
    def __init__(self, executor=None, description=None, inputs=None, inputs_from=None, extensions=None, output=None):
        if executor:
            verify_type(executor, Executor)
        self.executor = executor
        self.description = description
        self.inputs = inputs or []
        self.inputs_from = inputs_from or []
        self.extensions = extensions or []
        self.output = output
        self.hooks = []

    def command_as_str(self, filter=None):
        def apply_extensions(extensions):
            for extension in extensions:
                verify_type_or_subclass(extension, Extension)
                if isclass(extension):
                    extension = extension()
                extension.apply_to_phase(self)
                extension.apply_to_executor(self.executor)
                apply_extensions(extension.extensions)
        
        apply_extensions(self.extensions)

        for hook in self.hooks:
            hook(self)

        return self.executor.command_as_str(filter)
