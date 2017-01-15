# -*- coding: utf-8 -*-
#
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

from .version import VERSION
from .utils.types import verify_type
from .utils.argparse import ArgumentParser
from .utils.messages import error
from .utils.collections import StrictList, StrictDict
from StringIO import StringIO
from collections import OrderedDict
import threading, sys, inspect, os

_thread_locals = threading.local()

def new_context(**kwargs):
    """
    Creates a new context and calls :func:`configure_context` on it.
    
    If there already is a context in this thread, our new context will be a child of that context.

    :param root_path: the root of the input/output directory structure; defaults to the directory
                      in which the calling script resides
    :type root_path: string or function
    :param input_path_relative: the default input path relative to the root; defaults to the root
                                itself
    :type input_path_relative: string or function
    :param output_path_relative: the default base output path relative to the root; defaults to
                                 'build'
    :type output_path_relative: string or function
    :param binary_path_relative: the default binary output base path relative to the output path;
                                 defaults to 'bin'
    :type binary_path_relative: string or function
    :param object_path_relative: the default object output base path relative to the output path;
                                 defaults to 'obj'
    :type object_path_relative: string or function
    :param source_path_relative: the default source output base path relative to the output path;
                                 defaults to 'src'
    :type source_path_relative: string or function
    :param name: optional name to use for descriptions
    :type name: string or function
    :param frame: how many call frames to wind back to in order to find the calling script
    :type frame: integer
    """
    
    ctx = new_child_context()
    with ctx:
        configure_context(frame=2, **kwargs)
    return ctx

def new_child_context():
    """
    Creates a new context.
    
    If there already is a context in this thread, our new context will be a child of that context.
    
    :returns: new child context
    :rtype: :class:`Context`
    """
    
    ctx = Context._peek_thread_local()
    return Context(ctx)

def current_context(immutable=True):
    """
    Returns the current context if there is one, otherwise raises :class:`NoContextException`.
    
    By default, the context will be treated as immutable.
    
    :param immutable: set to False in order to allow changes to the context
    :type immutable: boolean
    :returns: current context
    :rtype: :class:`Context`
    """

    ctx = Context._peek_thread_local()
    if ctx is None:
        raise NoContextException()
    return Context(ctx, True) if immutable else ctx

def configure_context(root_path=None,
                      input_path_relative=None,
                      output_path_relative=None,
                      binary_path_relative=None,
                      object_path_relative=None,
                      source_path_relative=None,
                      name=None,
                      frame=1):
    """
    Configures the current context for builds.
    
    :param root_path: the root of the input/output directory structure; defaults to the directory
                      in which the calling script resides
    :type root_path: string or function
    :param input_path_relative: the default input path relative to the root; defaults to the root
                                itself
    :type input_path_relative: string or function
    :param output_path_relative: the default base output path relative to the root; defaults to
                                 'build'
    :type output_path_relative: string or function
    :param binary_path_relative: the default binary output base path relative to the output path;
                                 defaults to 'bin'
    :type binary_path_relative: string or function
    :param object_path_relative: the default object output base path relative to the output path;
                                 defaults to 'obj'
    :type object_path_relative: string or function
    :param source_path_relative: the default source output base path relative to the output path;
                                 defaults to 'src'
    :type source_path_relative: string or function
    :param name: optional name to use for descriptions
    :type name: string or function
    :param frame: how many call frames to wind back to in order to find the calling script
    :type frame: integer
    """

    from .utils.paths import join_path, base_path
    
    with current_context(False) as ctx:
        ctx.cli.args, _ = _ArgumentParser(name, frame + 1).parse_known_args()
        ctx.cli.verbose = ctx.cli.args.verbose

        ctx.build.debug = ctx.cli.args.debug

        ctx.current.project_outputs = StrictDict(key_class='ronin.projects.Project', value_class=dict)

        if ctx.cli.args.variant:
            ctx.projects.default_variant = ctx.cli.args.variant
        
        if ctx.cli.args.set:
            for value in ctx.cli.args.set:
                if '=' not in value:
                    error(u"'--set' argument is not formatted as 'ns.k=v': '%s'" % value)
                    sys.exit(1)
                k, v = value.split('=', 2)
                if '.' not in k:
                    error(u"'--set' argument is not formatted as 'ns.k=v': '%s'" % value)
                    sys.exit(1)
                namespace, k = k.split('.', 2)
                namespace = getattr(ctx, namespace)
                setattr(namespace, k, v)
        
        if root_path is None:
            root_path = base_path(inspect.getfile(sys._getframe(frame)))

        ctx.paths.root = root_path
        ctx.paths.input = join_path(root_path, input_path_relative)
        ctx.paths.output = join_path(root_path, output_path_relative or 'build')
        ctx.paths.binary_relative = binary_path_relative or 'bin'
        ctx.paths.object_relative = object_path_relative or 'obj'
        ctx.paths.source_relative = object_path_relative or 'src'

class Context(object):
    """
    Keeps track of environmental and user configuration properties per run.
    
    Designed to be attached to a single thread. Supports nesting contexts within the thread: a
    child context will return its parent's properties if it does not define them itself. 
    
    If the context is immutable it will raise :class:`ImmutableContextException` if you try to
    modify any of the properties.
    """
    
    _LOCAL = ('_parent', '_immutable', '_namespaces', '_exit_hooks')
    
    def __init__(self, parent=None, immutable=False):
        """
        :param parent: parent context or None
        :type parent: :class:`Context`
        :param immutable: set to True to make immutable
        :type immutable: boolean
        """
        
        if parent:
            verify_type(parent, Context)
        self._parent = parent
        self._immutable = immutable
        self._namespaces = StrictDict(key_class=basestring, value_class=_Namespace)
        self._exit_hooks = StrictList(value_class='types.FunctionType')
    
    def __unicode__(self):
        f = StringIO()
        try:
            self._write(f)
            v = f.getvalue()
        finally:
            f.close()
        return v

    def __enter__(self):
        self._push_thread_local()
        return self
    
    def __exit__(self, the_type, value, traceback):
        for hook in self._exit_hooks:
            hook(self)
        self._pop_thread_local()

    def __getattr__(self, name):
        if name in self._LOCAL:
            raise RuntimeError('context not initialized?')
        namespace = self._namespaces.get(name)
        if namespace is None:
            namespace = _Namespace(name, self)
            self._namespaces[name] = namespace
        return namespace

    def __setattr__(self, name, value):
        if name not in self._LOCAL:
            raise IncorrectUseOfContextException('namespaces cannot be assigned values: "%s"' % name)
        super(Context, self).__setattr__(name, value)

    def get(self, name, default=None):
        """
        Gets a value from the context or ``default`` if undefined.
        
        Values of any type can be stored in the context.
        
        Note that if the value is defined and is None, then None is returned and *not* ``default``.
        
        :param name: name in the format "ns.k"
        :type name: string
        :param default: default value
        :returns: value, default, or None
        """
        
        if '.' not in name:
            return default
        namespace_name, name = name.split('.', 2)
        try:
            namespace = getattr(self, namespace_name)
            return getattr(namespace, name)
        except NotInContextException:
            return default

    def fallback(self, value, name, default=None):
        """
        If the value is not None, returns it. Otherwise works identically to :meth:`get`.

        :param value: value
        :param name: name in the format "key.property"
        :type name: string
        :param default: default value
        :returns: value, default, or None
        """
        
        if value is None:
            return self.get(name, default)
        return value
    
    def append_to_import_path(self, name, default=None):
        """
        Convenience method to append a property in the context, if it exists, to ``sys.path``.
        
        :param name: name in the format "key.property"
        :type name: string
        :param default: default value
        """
        
        path = self.get(name, default)
        if path is not None:
            sys.path.append(path)
    
    @property
    def _all(self):
        r = OrderedDict()
        if self._parent:
            r.update(self._parent._all)
        for namespace_name, namespace in sorted(self._namespaces.items()):
            for k, v in sorted(namespace._all_local.items()):
                r['%s.%s' % (namespace_name, k)] = v
        return r

    def _write(self, f):
        from .utils.strings import stringify
        for k, v in self._all.iteritems():
            if not k.startswith('_'):
                v = stringify(v)
                f.write(u'%s=%s\n' % (k, v))

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
        
        :returns: the current context or None
        :rtype: :class:`Context`
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
        
        :returns: the current context or None
        :rtype: :class:`Context`
        """
        
        try:
            _thread_locals.ronin_context_stack.pop()
        except AttributeError:
            return None

class ContextException(Exception):
    """
    Base class for context exceptions.
    """

    def __init__(self, message=None):
        super(ContextException, self).__init__(message)

class NoContextException(ContextException):
    """
    Attempted to access the current context but there is none.
    """
    
    def __init__(self, message=None):
        super(NoContextException, self).__init__(message)

class NotInContextException(ContextException):
    """
    Attempted to access a property that is not in the context.
    """

    def __init__(self, message=None):
        super(NotInContextException, self).__init__(message)

class ImmutableContextException(ContextException):
    """
    Attempted to modify an immutable context.
    """

    def __init__(self, message=None):
        super(ImmutableContextException, self).__init__(message)

class IncorrectUseOfContextException(ContextException):
    """
    Attempted to access a namespace instead of a property.
    """

    def __init__(self, message=None):
        super(IncorrectUseOfContextException, self).__init__(message)

class _Namespace(object):
    """
    Manages properties in a :class:`Context`.
    """
    
    _LOCAL = ('_name', '_context')
    
    def __init__(self, name, context):
        self._name = name
        self._context = context

    @property
    def _all(self):
        r = OrderedDict()
        if self._context._parent:
            parent = getattr(self._context._parent, self._name)
            r.update(parent._all)
        r.update(self._all_local)
        return r

    @property
    def _all_local(self):
        r = OrderedDict()
        for k, v in sorted(vars(self).items()):
            if (k not in self._LOCAL) and (not k.startswith('_')):
                r[k] = v
        return r

    def __getattr__(self, name):
        if name in self._LOCAL:
            raise RuntimeError('namespace not initialized?')
        if self._context._parent is None:
            raise NotInContextException(u'%s.%s' % (self._name, name))
        parent = getattr(self._context._parent, self._name)
        return getattr(parent, name)

    def __setattr__(self, name, value):
        if name not in self._LOCAL:
            try:
                if self._context._immutable:
                    raise ImmutableContextException()
            except AttributeError:
                pass
        super(_Namespace, self).__setattr__(name, value)

class _ContextStack(object):
    """
    Manages a stack of :class:`Context` instances.
    """
    
    def __init__(self):
        self._stack = StrictList(value_class=Context)
    
    def push(self, context):
        self._stack.append(context)
    
    def peek(self):
        return self._stack[-1] if len(self._stack) else None

    def pop(self):
        return self._stack.pop() if len(self._stack) else None

class _ArgumentParser(ArgumentParser):
    def __init__(self, name, frame):
        from .utils.strings import stringify
        name = stringify(name)
        description = (u'Build %s using Rōnin %s' % (name, VERSION)) if name is not None else u'Build using Rōnin %s' % VERSION
        prog = os.path.basename(inspect.getfile(sys._getframe(frame)))
        super(_ArgumentParser, self).__init__(description=description, prog=prog)
        self.add_argument('operation', nargs='*', default=['build'], help='"build", "clean", "ninja"')
        self.add_flag_argument('debug', help_true='enable debug build', help_false='disable debug build')
        self.add_argument('--variant', help='override default project variant (defaults to host platform, e.g. "linux64")')
        self.add_argument('--set', nargs='*', metavar='ns.k=v', help='set values in the context')
        self.add_flag_argument('verbose', help_true='enable verbose output', help_false='disable verbose output')
