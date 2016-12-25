
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
        for define, value in self.defines:
            command.define_symbol(define, value)

    def add_to_command_link(self, command):
        for path in self.library_paths:
            command.add_library_path(path)
        for library in self.libraries:
            command.add_library(library)
