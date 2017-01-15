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
from ..projects import Project
from ..utils.platform import which, platform_command

DEFAULT_WINDRES_COMMAND = 'windres'

def configure_binutils(windres_command=None):
    """
    Configures the current context's `binutils <https://sourceware.org/binutils/docs/binutils/>`__
    support.
    
    :param windres_command: ``windres`` command; defaults to "windres"
    :type windres_command: string|function
    """
    
    with current_context(False) as ctx:
        ctx.binutils.windres_command = windres_command or DEFAULT_WINDRES_COMMAND

def which_windres(command, platform, exception=True):
    """
    A specialized version of :func:`ronin.utils.platform.which` for ``windres``.
    
    Behind the scenes uses :func:`windres_platform_command`.
    
    :param command: ``windres`` command
    :type command: string|function
    :param platform: target platform or project
    :type platform: string|function|:class:`ronin.projects.Project`
    :param exception: set to False in order to return None upon failure, instead of raising an
                      exception
    :type exception: boolean
    :returns: absolute path to command
    :rtype: string
    :raises WhichException: if ``exception`` is True and could not find command
    """
    
    if platform:
        command = windres_platform_command(command, platform)
    return which(command, exception=exception)

def windres_platform_command(command, platform):
    """
    Finds the ``windres`` command name for a specific target platform. 
    
    Behind the scenes uses :func:`ronin.utils.platform.platform_command`.

    :param command: ``windres`` command
    :type command: string|function
    :param platform: target platform or project
    :type platform: string|function|:class:`ronin.projects.Project`
    :returns: command
    :rtype: string
    """
    
    if isinstance(platform, Project):
        platform = platform.variant
    return platform_command(command, platform)

class WindRes(ExecutorWithArguments):
    """
    ``windres`` command from `binutils <https://sourceware.org/binutils/docs/binutils
    /windres.html>`__.
    """
    
    def __init__(self, command=None, extension=None, platform=None):
        """
        :param command: ``windres`` command; default's to context's ``binutils.windres_command``
        :type command: string|function
        :extension extension: output extensions; defaults to 'o'
        :type extension: string|function
        :param platform: target platform or project
        :type platform: string|function|:class:`ronin.projects.Project`
        """
        
        super(WindRes, self).__init__()
        self.command = lambda ctx: which_windres(ctx.fallback(command, 'binutils.windres_command', DEFAULT_WINDRES_COMMAND),
                                                 platform)
        self.output_type = 'object'
        self.output_extension = extension or 'o'
        self.add_argument_unfiltered('$in')
        self.add_argument_unfiltered('-o', '$out')
    
    def output_format(self, value):
        self.add_argument('-O', value)
    
    def output_res(self):
        self.output_format('res')
        self.output_extension = 'res'

    def output_rc(self):
        self.output_format('rc')
        self.output_extension = 'rc'

    def output_coff(self):
        self.output_format('coff')
        self.output_extension = 'o'
