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
from ..utils.paths import join_path
from multiprocessing import cpu_count

DEFAULT_RUSTC_COMMAND = 'rustc'
DEFAULT_CARGO_COMMAND = 'cargo'

def configure_rust(rustc_command=None, cargo_command=None):
    """
    Configures the current context's `Rust <https://www.rust-lang.org/>`__ support.
    
    :param rustc_command: ``rustc`` command; defaults to "rustc"
    :type rustc_command: string|function
    :param cargo_command: ``cargo`` command; defaults to "cargo"
    :type cargo_command: string|function
    """
    
    with current_context(False) as ctx:
        ctx.rust.rustc_command = rustc_command or DEFAULT_RUSTC_COMMAND
        ctx.rust.cargo_command = cargo_command or DEFAULT_CARGO_COMMAND

class RustBuild(ExecutorWithArguments):
    """
    `Rust <https://www.rust-lang.org/>`__ build executor.
    
    The phase inputs are ".rs" source files. The phase output is an executable (the default), an
    ".so" or ".dll" shared library, or a static library (".a").
    """
    
    def __init__(self, command=None):
        """
        :param command: ``rustc`` command; defaults to the context's ``rust.rustc_command``
        :type command: string|function
        """
        
        super(RustBuild, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'rust.rustc_command', DEFAULT_RUSTC_COMMAND))
        self.add_argument_unfiltered('$in')
        self.add_argument_unfiltered('-o', '$out')
        self.hooks.append(_build_debug_hook)

    def enable_debug(self):
        self.add_argument('-g')

class CargoBuild(ExecutorWithArguments):
    """
    `Cargo <https://crates.io/>`__ executor for `Rust <https://www.rust-lang.org/>`__.
    
    The phase input is a "Cargo.toml" file.

    Cargo will be doing all the heavy lifting. You just want to make sure that Ninja knows when to
    rebuild, so set the phase's "output=" to equal your "[[bin]]" definition in Cargo.toml, and use
    "rebuild_on=" with the relevant source files.
    """
    
    def __init__(self, command=None, jobs=None):
        """
        :param command: ``cargo`` command; defaults to the context's ``rust.cargo_command``
        :type command: string|function
        :param jobs: number of jobs; defaults to cpu_count + 1
        :type jobs: integer
        """

        super(CargoBuild, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'rust.cargo_command', DEFAULT_CARGO_COMMAND))
        self.add_argument('build')
        self.add_argument_unfiltered('--manifest-path', '$in')
        if jobs is None:
            jobs = cpu_count() + 1
        self.jobs(jobs)
        self.hooks.append(_cargo_output_path_hook)
        self.hooks.append(_cargo_debug_hook)

    def enable_release(self):
        self.add_argument('--release')

    def jobs(self, value):
        self.add_argument('--jobs', value)

def _build_debug_hook(executor):
    with current_context() as ctx:
        if ctx.get('build.debug', False):
            executor.enable_debug()

def _cargo_output_path_hook(executor):
    with current_context() as ctx:
        debug = ctx.get('build.debug', False)
        ctx.current.phase.output_path = join_path(ctx.paths.root, 'target', 'debug' if debug else 'release')

def _cargo_debug_hook(executor):
    with current_context() as ctx:
        if not ctx.get('build.debug', False):
            executor.enable_release()
