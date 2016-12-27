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

from .contexts import new_context
from .projects import Project
from .ninja import NinjaFile
from .utils.argparse import ArgumentParser
from .utils.types import verify_type
from .utils.messages import announce, error
from traceback import print_exc
import sys, os, inspect

def cli(*projects, **kwargs):
    """
    Run the Ronin CLI on one or more projects.
    
    :param projects: :class:`Project` instances
    """
    
    frame = kwargs.get('frame', 2)
    args, _ = _ArgumentParser(projects, frame).parse_known_args()
    
    with new_context() as ctx:
        try:
            ctx.debug = args.debug
            ctx.verbose = args.verbose
                
            if args.variant:
                ctx.platform_variant = args.variant
            
            if args.context:
                l = len(args.context)
                if l % 2 == 1:
                    error("Number of '--context' arguments is not even (%d)" % l)
                    sys.exit(1)
                for i in xrange(0, l, 2):
                    k = args.context[i]
                    v = args.context[i + 1]
                    setattr(ctx, k, v)
    
            for project in projects:
                verify_type(project, Project)
                for hook in project.hooks:
                    hook(project)
    
            if ctx.verbose:
                sys.stdout.write(str(ctx))
    
            for operation in args.operation:
                if operation in ('build', 'clean', 'ninja'):
                    for project in projects:
                        announce('%s' % project)
                        ninja_file = NinjaFile(project)
        
                        if operation == 'build':
                            r = ninja_file.build()
                            if r != 0:
                                sys.exit(r)
                        elif operation == 'clean':
                            r = ninja_file.clean()
                            if r != 0:
                                sys.exit(r)
                        elif operation == 'ninja':
                            ninja_file.generate()
                else:
                    error("Unsupported operation: '%s'" % operation)
                    sys.exit(1)
        except Exception as ex:
            if ctx.get('verbose', False):
                print_exc()
            else:
                error(ex)
            sys.exit(1)

class _ArgumentParser(ArgumentParser):
    def __init__(self, projects, frame):
        description = 'Build %s using Ronin' % ', '.join([str(v) for v in projects])
        prog = os.path.basename(inspect.getfile(sys._getframe(frame)))
        super(_ArgumentParser, self).__init__(description=description, prog=prog)
        self.add_argument('operation', nargs='*', default=['build'], help='operation ("build", "clean", "ninja")')
        self.add_flag_argument('debug', help_true='enable debug build', help_false='disable debug build')
        self.add_argument('--variant', help='override default project variant (defaults to host platform, e.g. "linux64")')
        self.add_argument('--context', nargs='*', help='set a value in the context')
        self.add_flag_argument('verbose', help_true='enable verbose output', help_false='disable verbose output')
