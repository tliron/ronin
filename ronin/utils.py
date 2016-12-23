
from .contexts import current_context
from collections import OrderedDict
from subprocess import check_output, CalledProcessError
import os, platform
from glob import glob as _glob

def build_path(*values):
    values = stringify_list(values)
    values = [v for v in values if v is not None]
    return os.path.join(*values)

def base_path(value):
    return os.path.dirname(os.path.realpath(value))

def glob(value):
    with current_context() as ctx:
        return _glob(build_path(ctx.get('input_path'), value))

def which(value):
    try:
        return check_output(['which', value]).strip()
    except CalledProcessError:
        return None

def host_variant():
    return '%s%s' % (platform.system().lower(), 64 if platform.machine().endswith('64') else 32)

def dedup(values):
    return list(OrderedDict.fromkeys(values))

def stringify_list(value):
    return [stringify(v) for v in value]

def stringify(value):
    if value is None:
        return None
    elif hasattr(value, '__call__'):
        with current_context() as ctx:
            value = value(ctx)
        return stringify(value)
    else:
        return str(value)

def stringify_unique(values):
    values = stringify_list(values)
    return dedup(values)

def join_stringify_lambda(values, separator=' '):
    return lambda _: separator.join([stringify(v) for v in values])

