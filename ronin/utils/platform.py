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

from __future__ import absolute_import # so we can import 'platform'

from .strings import stringify
from ..contexts import current_context
from subprocess import check_output, CalledProcessError
import sys, platform

DEFAULT_WHICH_COMMAND = '/usr/bin/which'

def host_variant():
    return '%s%d' % (host_platform(), host_bits())

def host_platform():
    platform = sys.platform
    return _PLATFORMS.get(platform, platform)

def host_bits():
    # Note: platform.architecture() extracts the bits from the Python executable,
    # which is not we want here (we might be running 32bit Python on a 64bit OS)
    machine = platform.machine() # i386, x86_64, AMD64
    return 64 if machine.endswith('64') else 32

def which(value, exception=False):
    value = stringify(value)
    try:
        with current_context() as ctx:
            command = ctx.get('which_command', DEFAULT_WHICH_COMMAND)
        value = check_output([command, value]).strip()
        if not value:
            value = None
        return value
    except CalledProcessError:
        if exception:
            raise Exception('could not find %s' % value)
        return None

# See: https://docs.python.org/2/library/sys.html#sys.platform
_PLATFORMS = {
    'linux2': 'linux',
    'win32':  'win',
    'cygwin': 'cygwin',
    'darwin': 'osx',
    'os2':    'os2_', # underscore to separate from bits
    'riscos': 'riscos',
    'atheos': 'atheos'}
