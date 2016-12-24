
from .contexts import new_context
from .ninja import NinjaFile
from .utils.argparse import ArgumentParser
import sys, os, inspect

def cli(*projects, **kwargs):
    """
    Run the Ronin CLI on one or more projects.
    
    :param projects: :class:`Project` instances
    """
    
    frame = kwargs.get('frame', 2)
    args, _ = _ArgumentParser(projects, frame).parse_known_args()
    
    with new_context() as ctx:
        ctx.debug = args.debug
        ctx.verbose = args.verbose
            
        if args.variant:
            ctx.platform_variant = args.variant
        
        if args.context:
            l = len(args.context)
            if l % 2 == 1:
                print "ronin: Number of '--context' arguments is not even (%d)" % l
                sys.exit(1)
            for i in xrange(0, l, 2):
                k = args.context[i]
                v = args.context[i + 1]
                setattr(ctx, k, v)

        if ctx.verbose:
            sys.stdout.write(str(ctx))

        for operation in args.operation:
            if operation in ('build', 'clean', 'ninja'):
                for project in projects:
                    print "ronin: %s" % project
                    ninja_file = NinjaFile(project)
    
                    if operation == 'build':
                        r = ninja_file.build()
                        if r != 0:
                            sys.exit(r)
                    elif operation == 'clean':
                        r = ninja_file.clean()
                        if r != 0:
                            sys.exit(r)
                    elif operation == 'ninja':
                        ninja_file.generate()
            else:
                print "ronin: Unsupported operation: '%s'" % operation
                sys.exit(1)

class _ArgumentParser(ArgumentParser):
    def __init__(self, projects, frame):
        description = 'Build %s using Ronin' % ', '.join([str(v) for v in projects])
        prog = os.path.basename(inspect.getfile(sys._getframe(frame)))
        super(_ArgumentParser, self).__init__(description=description, prog=prog)
        self.add_argument('operation', nargs='*', default=['build'], help='operation ("build", "clean", "ninja")')
        self.add_flag_argument('debug', help_true='enable debug build', help_false='disable debug build')
        self.add_argument('--variant', help='override default project variant (defaults to host platform, e.g. "linux64")')
        self.add_argument('--context', nargs='*', help='set a value in the context')
        self.add_flag_argument('verbose', help_true='enable verbose output', help_false='disable verbose output')
