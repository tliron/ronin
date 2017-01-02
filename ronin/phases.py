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
from .utils.paths import join_path, change_extension
from .utils.strings import stringify
from inspect import isclass
import os
from ronin.contexts import current_context

class Phase(object):
    """
    A build phase.
    """
    
    def __init__(self,
                 executor=None,
                 description=None,
                 inputs=None,
                 inputs_from=None,
                 extensions=None,
                 output=None,
                 output_path=None,
                 output_strip_prefix=None,
                 output_transform=None,
                 rebuild_on=None,
                 rebuild_on_from=None,
                 build_if=None,
                 build_if_from=None):
        if executor:
            verify_type(executor, Executor)
        self.executor = executor
        self.description = description
        self.inputs = inputs or []
        self.inputs_from = inputs_from or []
        self.extensions = extensions or []
        self.output = output
        self.output_path = output_path
        self.output_strip_prefix = output_strip_prefix
        self.output_transform = output_transform
        self.rebuild_on = rebuild_on or []
        self.rebuild_on_from = rebuild_on_from or []
        self.build_if = build_if or []
        self.build_if_from = build_if_from or []
        self.vars = {}
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

    def get_output_path(self, default_output_path):
        output_path = self.output_path
        if output_path is None:
            output_type = self.executor.output_type
            with current_context() as ctx:
                output_path = ctx.get('paths.%s' % output_type)
            if output_path is None:
                output_path = join_path(default_output_path, ctx.get('paths.%s_relative' % output_type))
        return output_path

    def get_outputs(self, default_output_path, inputs):
        # Paths
        with current_context() as ctx:
            input_base = ctx.get('paths.input')
        output_path = self.get_output_path(default_output_path)

        # Extension
        output_extension = stringify(self.executor.output_extension)

        if self.output:
            # Combine all inputs into one output
            output_prefix = stringify(self.executor.output_prefix) or ''
            output = output_prefix + change_extension(self.output, output_extension)
            output = join_path(output_path, output)
            if self.output_transform:
                output = self.output_transform(output)
                
            return True, [output]
        elif inputs:
            # Each input matches an output
            
            # Strip prefix
            output_strip_prefix = self.output_strip_prefix
            if output_strip_prefix is None:
                output_strip_prefix = input_base
            if not output_strip_prefix.endswith(os.sep):
                output_strip_prefix += os.sep
            output_strip_prefix_length = len(output_strip_prefix)
    
            outputs = []            
            for input in inputs:
                output = input
                if output.startswith(output_strip_prefix):
                    output = output[output_strip_prefix_length:]
                output = change_extension(output, output_extension)
                output = join_path(output_path, output)
                if self.output_transform:
                    output = self.output_transform(output)
                outputs.append(output)
                
            return False, outputs
