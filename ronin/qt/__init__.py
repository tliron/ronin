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
from ..utils.paths import join_path_later
from ..utils.strings import interpolate_later

DEFAULT_MOC_COMMAND = 'moc'

def configure_qt(moc_command=None):
    """
    Configures the current context's `Qt <https://www.qt.io/>`__ support.
    
    :param moc_command: ``moc`` command; defaults to "moc"
    :type moc_command: string|function
    """
    
    with current_context(False) as ctx:
        ctx.qt.moc_command = moc_command or DEFAULT_MOC_COMMAND

class QtMetaObjectCompile(ExecutorWithArguments):
    """
    `Qt <https://www.qt.io/>`__ meta-object compile (moc) executor.
    
    The phase inputs are ".h" header files. The phase outputs are ".cpp" source files prefixed
    with "moc\_". 
    """
    
    def __init__(self, command=None):
        """
        :param command: ``moc`` command; defaults to the context's ``qt.moc_command``
        :type command: string|function
        """
        
        super(QtMetaObjectCompile, self).__init__()
        self.command = lambda ctx: which(ctx.fallback(command, 'qt.moc_command', DEFAULT_MOC_COMMAND))
        self.command_types = ['gcc_compile']
        self.output_type = 'source'
        self.output_extension = 'cpp'
        self.output_prefix = 'moc_'
        self.add_argument_unfiltered('-o$out')
        self.add_argument_unfiltered('$in')

    def add_include_path(self, *value):
        self.add_argument(interpolate_later('-I%s', join_path_later(*value)))

    def add_framework_path(self, *value):
        self.add_argument(interpolate_later('-F%s', join_path_later(*value)))

    def define(self, name, value=None):
        if value is None:
            self.add_argument(interpolate_later('-D%s', name))
        else:
            self.add_argument(interpolate_later('-D%s=%s', name, value))
