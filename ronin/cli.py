
from .contexts import new_context
from .ninja import NinjaFile
from .utils.argparse import ArgumentParser as BaseArgumentParser
import sys

class ArgumentParser(BaseArgumentParser):
    def __init__(self, projects):
        super(ArgumentParser, self).__init__(description='Build %s' % ', '.join([str(v) for v in projects]), prog='build.py')
        self.add_argument('operation', nargs='?', default='build', help='operation ("build", "generate", "run")')
        self.add_argument('--variant', help='override default project variant (defaults to host platform, e.g. "linux64")')
        self.add_argument('--context', nargs='*', help='set a value in the context')

def cli(*projects):
    """
    Run the Ronin CLI on one or more projects.
    
    :param projects: :class:`Project` instances
    """
    
    
    args, _ = ArgumentParser(projects).parse_known_args()
    
    with new_context() as ctx:
        if args.variant:
            ctx.platform_variant = args.variant
            
        if args.operation == 'build':
            for project in projects:
                ninja_file = NinjaFile(project)
                r = ninja_file.run()
                if r != 0:
                    sys.exit(r)
        if args.operation == 'generate':
            for project in projects:
                ninja_file = NinjaFile(project)
                ninja_file.generate()
        if args.operation == 'run':
            pass
        else:
            print "ronin: Unsupported operation: '%s'" % args.operation
            sys.exit(1)
