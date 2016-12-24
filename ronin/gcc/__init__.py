
from ..commands import CommandWithArguments
from ..contexts import current_context
from ..libraries import Libraries
from ..utils.strings import stringify, stringify_unique, join_stringify_lambda
from ..utils.paths import build_path
from ..utils.platform import which

def configure_gcc(ctx, command='gcc', ccache=True):
    ctx.gcc_command = _gcc_command(command, ccache)

class GccCommand(CommandWithArguments):
    """
    Base class for `gcc <https://gcc.gnu.org/>`__ commands.
    """
    
    def __init__(self):
        super(GccCommand, self).__init__()
        self.command = lambda ctx: ctx.get('gcc_command', _gcc_command())
        self.command_types = ()
        self.linker_arguments = []
        self.deps = 'gcc'
        self.add_argument('$in')
        self.add_argument('-o', '$out')

    def write(self, io):
        super(GccCommand, self).write(io)
        if self.linker_arguments:
            io.write(' -Wl,')
            io.write(','.join(stringify_unique(self.linker_arguments)))
    
    def set_output(self, value):
        self.add_argument('-o', value)
    
    # Compiler
    
    def compile_only(self):
        self.add_argument('-c')
    
    def add_include_path(self, *value):
        self.add_argument(lambda _: '-I%s' % build_path(*value))

    def standard(self, value):
        self.add_argument(lambda _: '-std=%s' % stringify(value))

    def define_symbol(self, value):
        self.add_argument(lambda _: '-D%s' % stringify(value))

    def enable_warning(self, value='all'):
        self.add_argument(lambda _: '-W%s' % stringify(value))

    def disable_warning(self, value):
        self.add_argument(lambda _: '-Wno-%s' % stringify(value))
    
    def set_machine(self, value):
        self.add_argument(lambda _: '-m%s' % stringify(value))

    def set_machine_bits(self, project):
        self.set_machine(lambda _: '32' if stringify(project.variant).endswith('32') else '64')

    def set_machine_tune(self, value):
        self.add_argument(lambda _: '-mtune=%s' % stringify(value))

    def set_machine_floating_point(self, value):
        self.add_argument(lambda _: '-mfpmath=%s' % stringify(value))

    def optimize(self, value):
        self.add_argument(lambda _: '-O%s' % stringify(value))

    def enable_debug(self):
        self.add_argument('-g')

    def enable_threads(self):
        self.add_argument('-pthreads')
    
    def add_libraries(self, *libraries):
        libraries = Libraries(*libraries)
        libraries.add_to_command(self)

    # Linker

    def add_library_path(self, *value):
        self.add_argument(lambda _: '-L%s' % build_path(*value))

    def add_library(self, value):
        self.add_argument(lambda _: '-l%s' % stringify(value))

    def add_linker_argument(self, value):
        self.linker_arguments.append(value)
    
    def link_dynamic(self):
        self.add_argument('-rdynamic')

    def undefine(self, value):
        self.add_argument('-u', value)

    def create_shared_library(self):
        self.add_argument('-shared')
        self.output_extension = 'so'

    def create_static_library(self):
        self.add_argument('-static')
        self.output_extension = 'a'

    def use_ld(self, value):
        self.add_argument(lambda _: '-fuse-ld=%s' % stringify(value))

    # Makefile
    
    def _makefile(self, value, arg=None):
        args = [lambda _: '-M%s' % stringify(value)]
        if arg is not None:
            args.append(arg)
        self.add_argument(*args)

    def create_makefile(self):
        self._makefile('D') # does not imply "-E"

    def create_makefile_ignore_system(self):
        self._makefile('MD')
    
    def create_makefile_only(self):
        self._makefile('') # implies "-E"

    def set_makefile_path(self, value):
        self._makefile('F', value)

class GccMakefile(GccCommand):
    """
    Base class for gcc commands that also create a makefile.
    """
    
    def __init__(self):
        super(GccMakefile, self).__init__()
        self.depfile = True
        self.create_makefile_ignore_system()
        self.set_makefile_path('$out.d')

class GccBuild(GccMakefile):
    """
    gcc command supporting both compilation and linking phases.
    """
    
    def __init__(self):
        super(GccBuild, self).__init__()
        self.command_types = ('compile', 'link')
        with current_context() as ctx:
            if getattr(ctx, 'debug', False):
                self.enable_debug()

class GccCompile(GccMakefile):
    """
    gcc command supporting compilation phase only.
    """

    def __init__(self):
        super(GccCompile, self).__init__()
        self.command_types = ('compile',)
        self.output_extension = 'o'
        self.compile_only()
        with current_context() as ctx:
            if getattr(ctx, 'debug', False):
                self.enable_debug()

class GccLink(GccCommand):
    """
    gcc command supporting linking phase only.
    """

    def __init__(self):
        super(GccLink, self).__init__()
        self.command_types = ('link',)

def _gcc_command(command='gcc', ccache=True):
    if ccache:
        r = which('/usr/lib/ccache/%s' % command)
        if r is None:
            r = which(command)
    else:
        r = which(command)
    return r
