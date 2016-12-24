
from inspect import isclass

class Library(object):
    """
    Base class for libraries.
    """
    
    def add_to_command(self, command):
        for command_type in command.command_types:
            getattr(self, 'add_to_command_%s' % command_type)(command)

class ExplicitLibrary(Library):
    """
    A library with explicitly stated data.
    """
    
    def __init__(self, include_paths=None, defines=None, library_paths=None, libraries=None):
        super(ExplicitLibrary, self).__init__()
        self.include_paths = include_paths or []
        self.defines = defines or []
        self.library_paths = library_paths or []
        self.libraries = libraries or []

    def add_to_command_compile(self, command):
        for path in self.include_paths:
            command.add_include_path(path)
        for define in self.defines:
            command.define_symbol(define)

    def add_to_command_link(self, command):
        for path in self.library_paths:
            command.add_library_path(path)
        for library in self.libraries:
            command.add_library(library)

class Libraries(object):
    """
    Manages a list of libraries, which can be either subclasses of :class:`Library` or instances
    of subclasses.
    """
    
    def __init__(self, *libraries):
        for library in libraries:
            if isclass(library):
                if not issubclass(library, Library):
                    raise AttributeError('not a subclass of %s: %s' % (Library.__name__, library.__name__))
            else:
                if not isinstance(library, Library):
                    raise AttributeError('not an instance of %s: %s' % (Library.__name__, library.__class__.__name__))
        
        self._libraries = libraries
    
    def add_to_command(self, command):
        for library in self._libraries:
            if isclass(library):
                library = library()
            library.add_to_command(command)
