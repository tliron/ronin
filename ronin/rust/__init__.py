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
from ..utils.platform import which
from ..utils.strings import join_later, interpolate_later

DEFAULT_RUSTC_COMMAND = 'rustc'

def configure_rust(command=None):
    with current_context(False) as ctx:
        ctx.rust.command = command or DEFAULT_RUSTC_COMMAND

class RustBuild(ExecutorWithArguments):
    """
    Base class for `Rust <https://www.rust-lang.org/>`__ executors.
    """
    
    def __init__(self, command=None):
        super(RustBuild, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'rust.command', DEFAULT_RUSTC_COMMAND))
        self.add_argument_unfiltered('$in')
        self.add_argument_unfiltered('-o', '$out')
        self.hooks.append(_debug_hook)

def _debug_hook(executor):
    with current_context() as ctx:
        if ctx.get('build.debug', False):
            executor.enable_debug()
