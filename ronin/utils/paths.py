
from .strings import stringify, stringify_list
from ..contexts import current_context
from glob import glob as _glob
import os

def join_path(*values):
    values = stringify_list(values)
    values = [v for v in values if v is not None]
    return os.path.join(*values)

def base_path(value):
    value = stringify(value)
    return os.path.dirname(os.path.realpath(value))

def input_path(value):
    with current_context() as ctx:
        return join_path(ctx.get('input_path'), value)

def glob(value):
    value = stringify(value)
    with current_context() as ctx:
        return _glob(join_path(ctx.get('input_path'), value))

def change_extension(value, new_extension):
    value = stringify(value)
    new_extension = stringify(new_extension)
    if new_extension is None:
        return value
    dot = value.rfind('.')
    if dot != -1:
        value = value[:dot]
    return '%s.%s' % (value, new_extension)
