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

DEFAULT_PLATFORM_PREFIXES = {
    'linux64': 'x86_64-linux-gnu-',
    'linux32': 'x86_64-linux-gnu-', #'i686-linux-gnu-',
    'win64': 'x86_64-w64-mingw32-',
    'win32': 'i686-w64-mingw32-'}

def host_platform():
    return '%s%d' % (host_operating_system(), host_bits())

def host_operating_system():
    operating_system = sys.platform
    return _OPERATING_SYSTEMS.get(operating_system, operating_system)

def host_bits():
    # Note: platform.architecture() extracts the bits from the Python executable,
    # which is not we want here (we might be running 32bit Python on a 64bit OS)
    machine = platform.machine() # i386, x86_64, AMD64
    return 64 if machine.endswith('64') else 32

def which(command, exception=False):
    command = stringify(command)
    try:
        with current_context() as ctx:
            which_command = ctx.get('which_command', DEFAULT_WHICH_COMMAND)
        command = check_output([which_command, command]).strip()
        if not command:
            command = None
        return command
    except CalledProcessError:
        if exception:
            raise Exception("'which' could not find '%s'" % command)
        return None

def platform_prefixes():
    with current_context() as ctx:
        return ctx.get('platform_prefixes', DEFAULT_PLATFORM_PREFIXES)

def platform_prefix(platform):
    platform = stringify(platform)
    return stringify(platform_prefixes().get(platform, ''))

def platform_command(command, platform):
    command = stringify(command)
    return '%s%s' % (platform_prefix(platform), command)

def platform_executable_extension(platform):
    platform = stringify(platform)
    if platform in ('win64', 'win32'):
        return 'exe'
    return None

def platform_shared_library_extension(platform):
    platform = stringify(platform)
    if platform in ('win64', 'win32'):
        return 'dll'
    return 'so'

def platform_shared_library_prefix(platform):
    platform = stringify(platform)
    if platform in ('win64', 'win32'):
        return None
    return 'lib'

# See: https://docs.python.org/2/library/sys.html#sys.platform
_OPERATING_SYSTEMS = {
    'linux2': 'linux',
    'win32':  'win',
    'cygwin': 'cygwin',
    'darwin': 'osx',
    'os2':    'os2_', # underscore to separate from bits
    'riscos': 'riscos',
    'atheos': 'atheos'}
