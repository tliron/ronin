
from inspect import isclass

def verify_type(value, the_type):
    if not isinstance(value, the_type):
        raise AttributeError('not an instance of %s: %s' % (the_type.__name__, value.__class__.__name__)) 

def verify_subclass(value, the_type):
    if not issubclass(value, the_type):
        raise AttributeError('not a subclass of %s: %s' % (the_type.__name__, value.__name__))

def verify_type_or_subclass(value, the_type):
    if isclass(value):
        verify_subclass(value, the_type)
    else:
        verify_type(value, the_type)
