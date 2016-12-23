
from .contexts import current_context
from .utils import build_path, stringify, which
from cStringIO import StringIO
from os import makedirs
from subprocess import check_call, CalledProcessError
import sys

def configure_ninja(ctx, command='ninja', file_name='build.ninja', columns=100):
    ctx.ninja_command = which(command)
    ctx.ninja_file_name = file_name
    ctx.ninja_file_columns = columns

class NinjaFile(object):
    """
    Manages a `Ninja build system <https://ninja-build.org/>`__ file.
    """
    
    def __init__(self, project):
        self._project = project
    
    def __str__(self):
        io = StringIO()
        try:
            self.write(io)
            v = io.getvalue()
        finally:
            io.close()
        return v
    
    def write_line(self, io, line=''):
        #ctx.ninja_file_columns
        io.write('%s\n' % line)
    
    def write(self, io):
        for rule_name, rule in self._project.rules.iteritems():
            self.write_line(io)
            self.write_line(io, 'rule %s' % rule_name)
            description = stringify(rule.description)
            if description is not None:
                self.write_line(io, '  description = %s' % description)
            self.write_line(io, '  command = %s' % rule.command)
            if rule.command.depfile:
                self.write_line(io, '  depfile = $out.d')
            deps = stringify(rule.command.deps)
            if deps is not None:
                self.write_line(io, '  deps = %s' % deps)
            if rule.inputs:
                with current_context() as ctx:
                    inputs = [build_path(ctx.get('input_path'), v) for v in rule.inputs]
                    output = ctx.get('binary_path')
                    if output is None:
                        output = build_path(self.base_path, ctx.get('binary_path_relative'))
                    output = build_path(output, rule.output)
                self.write_line(io)
                self.write_line(io, 'build %s: %s %s' % (output, rule_name, ' '.join(inputs)))

    @property
    def base_path(self):
        with current_context() as ctx:
            return build_path(ctx.output_path, self._project.variant)

    @property
    def path(self):
        with current_context() as ctx:
            return build_path(self.base_path, ctx.get('ninja_file_name', 'build.ninja'))

    def generate(self):
        base_path = self.base_path
        path = self.path
        print "ronin: Generating '%s'" % path
        try:
            makedirs(base_path)
        except OSError:
            pass
        with open(path, 'w') as io:
            self.write(io)

    def run(self):
        self.generate()
        with current_context() as ctx:
            try:
                check_call([stringify(ctx.get('ninja_command', 'ninja')), '-C', self.base_path])
            except CalledProcessError as e:
                return e.returncode
        return 0

    def delegate(self):
        sys.exit(self.run())
