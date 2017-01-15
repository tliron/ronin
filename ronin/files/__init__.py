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

DEFAULT_CP_COMMAND = 'cp'

def configure_files(copy_command=None):
    """
    Configures the current context's files support.
    
    :param copy_command: copy command; defaults to "cp"
    :type copy_command: string|function
    """
    
    with current_context(False) as ctx:
        ctx.files.cp_command = copy_command or DEFAULT_CP_COMMAND

class Copy(ExecutorWithArguments):
    """
    File copy executor.
    
    The phase inputs are copied to the phase outputs.
    
    Use the phase's ``input_path_relative`` if you need to strip the input paths from the output
    paths.
    """
    
    def __init__(self, command=None):
        """
        :param command: ``cp`` command; default's to context's ``files.cp_command``
        :type command: string|function
        """
        
        super(Copy, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'files.cp_command', DEFAULT_CP_COMMAND))
        self.add_argument_unfiltered('$in')
        self.add_argument_unfiltered('$out')
