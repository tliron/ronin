
from .utils.types import verify_type
from cStringIO import StringIO
from collections import OrderedDict
import threading

_thread_locals = threading.local()

def new_build_context(*args, **kwargs):
    """
    Creates a new context and calls :code:`configure_build` on it.
    """
    
    from .configuration import configure_build
    ctx = new_context()
    ctx._push_thread_local()
    try:
        configure_build(*args, frame=2, **kwargs)
    finally:
        Context._pop_thread_local()
    return ctx

def new_context():
    """
    Creates a new context.
    
    If there already is a context in this thread, our new context will be a child of that context.
    """
    
    ctx = Context._peek_thread_local()
    return Context(ctx)

def current_context(immutable=True):
    """
    Uses the current context if there is one. If there is none, raises a
    :class:`NoContextException`.
    
    By default, the context will be treated as immutable.
    """

    ctx = Context._peek_thread_local()
    if ctx is None:
        raise NoContextException()
    return Context(ctx, True) if immutable else ctx

class Context(object):
    """
    Keeps track of environmental and user configuration properties per run.
    
    Designed to be attached to a single thread. Supports nesting contexts within the thread: a
    child context will return its parent's properties if it does not define them itself. 
    
    If the context is immutable it will raise :class:`ImmutableContextException` if you try to
    modify any of the properties.
    """
    
    LOCAL = ('_parent', '_immutable')
    
    def __init__(self, parent=None, immutable=False):
        if parent:
            verify_type(parent, Context)
        self._parent = parent
        self._immutable = immutable
    
    def __str__(self):
        io = StringIO()
        try:
            self.write(io)
            v = io.getvalue()
        finally:
            io.close()
        return v

    def get(self, name, default=None):
        try:
            return getattr(self, name)
        except NotInContextException:
            return default

    def fallback(self, value, name, default=None):
        if value is None:
            return self.get(name, default)
        return value
    
    def write(self, io):
        for k, v in self._all.iteritems():
            io.write('%s=%s\n' % (k, v))

    @property
    def _all(self):
        r = OrderedDict()
        if self._parent:
            r.update(self._parent._all)
        for k, v in sorted(vars(self).items()):
            if k not in Context.LOCAL:
                r[k] = v
        return r

    def _push_thread_local(self):
        """
        Attaches this context to the current thread by pushing it on the stack.
        """

        try:
            stack = _thread_locals.ronin_context_stack
        except AttributeError:
            stack = _ContextStack()
            _thread_locals.ronin_context_stack = stack
        stack.push(self)

    @staticmethod
    def _peek_thread_local():
        """
        Gets the context attached to the current thread if there is one, which will be the top
        context on the stack.
        """

        try:
            return _thread_locals.ronin_context_stack.peek()
        except AttributeError:
            return None

    @staticmethod
    def _pop_thread_local():
        """
        Removes the context attached to the current thread if there is one, which will be the top
        context on the stack.
        """
        
        try:
            _thread_locals.ronin_context_stack.pop()
        except AttributeError:
            return None


    def __enter__(self):
        self._push_thread_local()
        return self
    
    def __exit__(self, the_type, value, traceback):
        self._pop_thread_local()

    def __getattr__(self, name):
        if name in Context.LOCAL:
            raise AttributeError(name)

        if self._parent is None:
            raise NotInContextException(name)

        return getattr(self._parent, name)

    def __setattr__(self, name, value):
        if name in Context.LOCAL:
            super(Context, self).__setattr__(name, value)
            return

        try:
            if self._immutable:
                raise ImmutableContextException()
        except AttributeError:
            pass

        super(Context, self).__setattr__(name, value)

class ContextException(Exception):
    """
    Base class for context excpetions.
    """

    def __init__(self, message=None):
        super(ContextException, self).__init__(message)

class NoContextException(ContextException):
    def __init__(self, message=None):
        super(NoContextException, self).__init__(message)

class NotInContextException(ContextException):
    def __init__(self, message=None):
        super(NotInContextException, self).__init__(message)

class ImmutableContextException(ContextException):
    def __init__(self, message=None):
        super(ImmutableContextException, self).__init__(message)

class _ContextStack(object):
    """
    Manages a stack of :class:`Context` instances.
    """
    
    def __init__(self):
        self._stack = []
    
    def push(self, context):
        self._stack.append(context)
    
    def peek(self):
        return self._stack[-1] if len(self._stack) else None

    def pop(self):
        return self._stack.pop() if len(self._stack) else None
