# -*- coding: utf-8 -*-
#
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
from .projects import Project
from .ninja import NinjaFile
from .utils.strings import stringify_list
from .utils.types import verify_type
from .utils.messages import announce, error
from traceback import print_exc
from subprocess import check_call, CalledProcessError
import sys


def cli(*projects):
    """
    Delegates control to the Rōnin CLI on one or more projects.
    
    Note that the process is expected to exit after running the CLI, so this should only normally
    be used as the last call of your build script.
    
    :param projects: projects
    :type projects: [:class:`~ronin.projects.Project`] 
    """
    
    try:
        for project in projects:
            verify_type(project, Project)
            for hook in project.hooks:
                hook(project)

        with current_context() as ctx:
            if ctx.get('cli.verbose', False):
                sys.stdout.write(unicode(ctx))
            operations = ctx.cli.args.operation

        for operation in operations:
            if operation in ('build', 'clean', 'ninja'):
                for project in projects:
                    announce(u'{}'.format(project))
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
                error(u"Unsupported operation: '{}'".format(operation))
                sys.exit(1)

        for _, run in sorted(project.run.items()):
            run = stringify_list(run)
            run_string = ' '.join(run)
            announce(u"Running: '{}'".format(run_string))
            try:
                check_call(run)
            except CalledProcessError as ex:
                error(u"'{}' failed with code: {:d}".format(run_string, ex.returncode))
                sys.exit(ex.returncode)
    except BaseException as ex:
        if isinstance(ex, SystemExit):
            code = ex.code
        else:
            code = 1
        if ctx.get('cli.verbose', False):
            print_exc()
        elif not isinstance(ex, SystemExit):
            error(ex)
        sys.exit(code)
