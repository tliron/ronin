
from .collections import dedup
from ..contexts import current_context

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
