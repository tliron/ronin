
from __future__ import absolute_import # so we can import 'platform'

from .strings import stringify
from subprocess import check_output, CalledProcessError
import sys, platform

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

def which(value):
    value = stringify(value)
    try:
        return check_output(['which', value]).strip()
    except CalledProcessError:
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
