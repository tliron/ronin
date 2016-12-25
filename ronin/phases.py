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

from .commands import Command
from .utils.types import verify_type

class Phase(object):
    """
    A build phase.
    """
    
    def __init__(self, command=None, description=None, inputs=None, inputs_from=None, output=None):
        if command:
            verify_type(command, Command)
        self.command = command
        self.description = description
        self.inputs = inputs or []
        self.inputs_from = inputs_from or []
        self.output = output
