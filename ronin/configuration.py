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
from .utils.paths import join_path, base_path
import inspect, sys

def configure_build(root_path=None,
                    input_path_relative=None,
                    output_path_relative=None,
                    binary_path_relative=None,
                    object_path_relative=None,
                    frame=1):
    with current_context(False) as ctx:
        if root_path is None:
            root_path = base_path(inspect.getfile(sys._getframe(frame)))
        ctx.input_path = join_path(root_path, input_path_relative)
        ctx.output_path = join_path(root_path, output_path_relative or 'build')
        ctx.binary_path_relative = binary_path_relative or 'bin'
        ctx.object_path_relative = object_path_relative or 'obj'
        ctx._results = {}
