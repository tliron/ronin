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

def configure_platform(prefixes=None, which_command=None):
    """
    Configures the current context's platform support.
    
    :param prefixes: overrides for the default platform prefixes; unspecified keys will remain
                     unchanged from their defaults
    :type prefixes: dict of string, string or function
    :param which_command: absolute path to :func:`which` command; defaults to "/usr/bin/which"
    :type which_command: string|function
    """
    
    with current_context(False) as ctx:
        ctx.platform.prefixes = DEFAULT_PLATFORM_PREFIXES.copy()
        if platform_prefixes:
            ctx.platform.prefixes.update(prefixes)
        ctx.platform.which_command = which_command or DEFAULT_WHICH_COMMAND

def platform_command(command, platform):
    """
    The command prefixed for the platform, from :func:`platform_prefixes`.
    
    :param command: command
    :type command: string|function
    :param platform: platform
    :type platform: string|function
    :returns: prefixed command
    :rtype: string
    """

    command = stringify(command)
    return '%s%s' % (platform_prefix(platform), command)

def platform_executable_extension(platform):
    """
    The executable extension for the platform, e.g. ``exe`` for windows and None for other
    platforms.
    
    :param platform: platform
    :type platform: string|function
    :returns: executable extension or None
    :rtype: string
    """
    
    platform = stringify(platform)
    if platform in ('win64', 'win32'):
        return 'exe'
    return None

def platform_shared_library_extension(platform):
    """
    The shared library extension for the platform, e.g. ``dll`` for windows and ``so`` for other
    platforms.
    
    :param platform: platform
    :type platform: string|function
    :returns: shared library extension or None
    :rtype: string
    """

    platform = stringify(platform)
    if platform in ('win64', 'win32'):
        return 'dll'
    return 'so'

def platform_shared_library_prefix(platform):
    """
    The shared library extension for the platform, e.g. ``lib`` for \*nix and None for Windows.
    
    :param platform: platform
    :type platform: string|function
    :returns: shared library prefix or None
    :rtype: string
    """

    platform = stringify(platform)
    if platform in ('win64', 'win32'):
        return None
    return 'lib'

def platform_prefixes():
    """
    The current context's ``platform.prefixes`` or the defaults. See also
    :func:`configure_platform`.
    
    :returns: platform prefixes
    :rtype: dict of string, string or function
    """
    
    with current_context() as ctx:
        return ctx.get('platform.prefixes', DEFAULT_PLATFORM_PREFIXES)

def platform_prefix(platform):
    """
    The prefix for the platform, from :func:`platform_prefixes`.
    
    :param platform: platform
    :type platform: string|function
    :returns: platform prefixes or ''
    :rtype: string
    """

    platform = stringify(platform)
    return stringify(platform_prefixes().get(platform, ''))

def host_platform():
    """
    The platform for the host machine on which we are running. A combination of
    :func:`host_operating_system_prefix` and :func:`host_bits`.

    :returns: host platform
    :rtype: string
    """
    
    return '%s%d' % (host_operating_system_prefix(), host_bits())

def host_operating_system_prefix():
    """
    The operating system prefix for the host machine on which we are running.

    :returns: operating system
    :rtype: string
    """

    operating_system = sys.platform
    return _OPERATING_SYSTEMS_PREFIXES.get(operating_system, operating_system)

def host_bits():
    """
    The bits (64 or 32) for the host machine on which we are running.

    :returns: bits
    :rtype: integer
    """

    # Note: platform.architecture() extracts the bits from the Python executable,
    # which is not we want here (we might be running 32bit Python on a 64bit OS)
    machine = platform.machine() # i386, x86_64, AMD64
    return 64 if machine.endswith('64') else 32

def which(command, exception=True):
    """
    Finds the absolute path to a command on this host machine.
    
    Works by invoking the operating system's ``which`` command, which configured via the context's
    ``platform.which_command``. See also :func:`configure_which`.

    :param command: command
    :type command: string|function
    :param exception: set to False in order to return None upon failure, instead of raising an
                      exception
    :type exception: boolean
    :returns: absolute path to command
    :rtype: string
    :raises WhichException: if ``exception`` is True and could not find command
    """

    command = stringify(command)
    try:
        with current_context() as ctx:
            which_command = ctx.get('platform.which_command', DEFAULT_WHICH_COMMAND)
            which_command = stringify(which_command)
        command = check_output([which_command, command]).strip()
        if not command:
            if exception:
                raise WhichException(u"could not find '%s'" % command)
            return None
        return command
    except CalledProcessError:
        if exception:
            raise WhichException(u"could not find '%s'" % command)
        return None

class WhichException(Exception):
    """
    :func:`which` could not find the command.
    """

    def __init__(self, message=None):
        super(WhichException, self).__init__(message)

# See: https://docs.python.org/2/library/sys.html#sys.platform
_OPERATING_SYSTEMS_PREFIXES = {
    'linux2': 'linux',
    'win32':  'win',
    'cygwin': 'cygwin',
    'darwin': 'osx',
    'os2':    'os2_', # underscore to separate from bits
    'riscos': 'riscos',
    'atheos': 'atheos'}
