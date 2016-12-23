
from .arguments import ArgumentParser as BaseArgumentParser
from .ninja import NinjaFile
import sys

class ArgumentParser(BaseArgumentParser):
    def __init__(self, project):
        super(ArgumentParser, self).__init__(description='Build %s' % project, prog='build.py')
        self.add_argument('operation', nargs='?', default='build', help='operation (build, generate)')
        self.add_argument('--variant', help='variant (defaults to host platform)')

def build_cli(project):
    args, _ = ArgumentParser(project).parse_known_args()
    
    if args.operation == 'build':
        ninja_file = NinjaFile(project)
        ninja_file.delegate()
    if args.operation == 'generate':
        ninja_file = NinjaFile(project)
        ninja_file.generate()
    else:
        print 'ronin: unsupported operation: %s' % args.operation
        sys.exit(1)
