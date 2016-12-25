
from .collections import dedup
from ..contexts import current_context

def stringify_list(values):
    return [stringify(v) for v in values]

def stringify(value):
    if value is None:
        return None
    elif hasattr(value, '__call__'):
        with current_context() as ctx:
            value = value(ctx)
        return stringify(value)
    else:
        return str(value)

def bool_stringify(value):
    if value is None:
        return False
    elif hasattr(value, '__call__'):
        with current_context() as ctx:
            value = value(ctx)
        return bool_stringify(value)
    else:
        if isinstance(value, bool):
            return value
        return str(value).lower() == 'true'

def stringify_unique(values):
    values = stringify_list(values)
    return dedup(values)

def join_stringify_lambda(values, separator=' '):
    return lambda _: separator.join(stringify_list(values))
