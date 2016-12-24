
from __future__ import absolute_import # so we can import 'platform'

from subprocess import check_output, CalledProcessError
import platform

def host_variant():
    return '%s%s' % (platform.system().lower(), 64 if platform.machine().endswith('64') else 32)

def which(value):
    try:
        return check_output(['which', value]).strip()
    except CalledProcessError:
        return None
