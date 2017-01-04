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
from .utils.argparse import ArgumentParser
from .utils.paths import join_path, base_path
from .utils.platform import DEFAULT_WHICH_COMMAND, DEFAULT_PLATFORM_PREFIXES
from .utils.messages import error
import inspect, sys, os

def configure_build(root_path=None,
                    input_path_relative=None,
                    output_path_relative=None,
                    binary_path_relative=None,
                    object_path_relative=None,
                    source_path_relative=None,
                    which_command=None,
                    platform_prefixes=None,
                    name=None,
                    frame=1):
    with current_context(False) as ctx:
        ctx.cli.args, _ = _ArgumentParser(name, frame + 1).parse_known_args()
        ctx.cli.verbose = ctx.cli.args.verbose

        ctx.build.debug = ctx.cli.args.debug

        ctx.current.project_outputs = {}

        if ctx.cli.args.variant:
            ctx.projects.default_variant = ctx.cli.args.variant
        
        if ctx.cli.args.set:
            for value in ctx.cli.args.set:
                if '=' not in value:
                    error("'--set' argument is not formatted as 'ns.k=v': '%s'" % value)
                    sys.exit(1)
                k, v = value.split('=', 2)
                if '.' not in k:
                    error("'--set' argument is not formatted as 'ns.k=v': '%s'" % value)
                    sys.exit(1)
                namespace, k = k.split('.', 2)
                namespace = getattr(ctx, namespace)
                setattr(namespace, k, v)
        
        if root_path is None:
            root_path = base_path(inspect.getfile(sys._getframe(frame)))

        ctx.paths.root = root_path
        ctx.paths.input = join_path(root_path, input_path_relative)
        ctx.paths.output = join_path(root_path, output_path_relative or 'build')
        ctx.paths.binary_relative = binary_path_relative or 'bin'
        ctx.paths.object_relative = object_path_relative or 'obj'
        ctx.paths.source_relative = object_path_relative or 'src'
        
        ctx.platform.which_command = which_command or DEFAULT_WHICH_COMMAND
        ctx.platform.prefixes = DEFAULT_PLATFORM_PREFIXES.copy()
        if platform_prefixes:
            ctx.platform.prefixes.update(platform_prefixes)

class _ArgumentParser(ArgumentParser):
    def __init__(self, name, frame):
        description = ('Build %s using Ronin') % name if name is not None else 'Build using Ronin'
        prog = os.path.basename(inspect.getfile(sys._getframe(frame)))
        super(_ArgumentParser, self).__init__(description=description, prog=prog)
        self.add_argument('operation', nargs='*', default=['build'], help='"build", "clean", "ninja"')
        self.add_flag_argument('debug', help_true='enable debug build', help_false='disable debug build')
        self.add_argument('--variant', help='override default project variant (defaults to host platform, e.g. "linux64")')
        self.add_argument('--set', nargs='*', metavar='ns.k=v', help='set values in the context')
        self.add_flag_argument('verbose', help_true='enable verbose output', help_false='disable verbose output')
