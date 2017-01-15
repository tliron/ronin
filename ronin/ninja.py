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

from .contexts import current_context, new_child_context
from .projects import Project
from .phases import Phase
from .executors import Executor
from .utils.paths import join_path
from .utils.strings import stringify, stringify_list
from .utils.platform import which
from .utils.collections import dedup, StrictDict
from .utils.types import verify_type
from .utils.messages import announce
from StringIO import StringIO
from os import makedirs
from subprocess import check_call, CalledProcessError
from datetime import datetime
from textwrap import wrap
import sys, os, io

# See:
# https://ninja-build.org/manual.html#_ninja_file_reference
# https://github.com/ninja-build/ninja/blob/master/misc/ninja_syntax.py

DEFAULT_NAME = 'build'
DEFAULT_ENCODING = 'utf-8'
DEFAULT_COLUMNS = 100

def configure_ninja(ninja_command=None, encoding=None, file_name=None, columns=None, strict=None):
    """
    :param ninja_command: ``ninja`` command; defaults to "ninja"
    :type ninja_command: string|function
    :param encoding: Ninja file encoding; defaults to "utf-8"
    :type encoding: string|function
    :param file_name: Ninja filename (without ".ninja" extension); defaults to "build"
    :type file_name: string|function
    :param columns: number of columns in Ninja file; defaults to 100
    :type columns: integer
    :param strict: strict column mode; defaults to False
    :type strict: boolean
    """
    
    with current_context(False) as ctx:
        ctx.ninja.command = ninja_command
        ctx.ninja.encoding = encoding
        ctx.ninja.file_name = file_name
        ctx.ninja.file_columns = columns
        ctx.ninja.file_strict = strict

def escape(value):
    """
    Escapes special characters for literal inclusion in a Ninja file.
    
    :param value: literal value to escape
    :type value: string|function
    :returns: escaped value
    :rtype: string
    """
    
    value = stringify(value)
    return value.replace('$', '$$')

def pathify(value):
    """
    Escapes special characters for inclusion in a Ninja file where paths are expected.
    
    :param value: path value to escape
    :type value: string|function
    :returns: escaped value
    :rtype: string
    """
    
    value = stringify(value)
    return value.replace('$ ', '$$ ').replace(' ', '$ ').replace(':', '$:')

class NinjaFile(object):
    """
    Manages a `Ninja build system <https://ninja-build.org/>`__ file.
    """
    
    def __init__(self, project, command=None, encoding=None, file_name=None, columns=None, strict=None):
        """
        :param project: project
        :type project: :class:`ronin.projects.Project`
        :param command: Ninja command; defaults to the context's ``ninja.command``
        :type command: string|function
        :param encoding: Ninja file encoding; defaults to the context's ``ninja.encoding``
        :type encoding: string|function
        :param file_name: Ninja filename (without ".ninja" extension); defaults to the context's
                          ``ninja.file_name``
        :type file_name: string|function
        :param columns: number of columns in Ninja file; defaults to the context's ``ninja.columns``
        :type columns: integer
        :param strict: strict column mode; defaults to the context's ``ninja.strict``
        :type strict: boolean
        """
        
        verify_type(project, Project)
        self._project = project
        self.command = command
        self.encoding = encoding
        self.file_name = file_name
        self.columns = columns
        self.strict = strict
    
    def __unicode__(self):
        f = StringIO()
        try:
            self.write(f)
            v = f.getvalue()
        finally:
            f.close()
        return v
    
    @property
    def file_name(self):
        """
        The Ninja file name, not including the path. The ``file_name`` if set, or else the project's
        ``file_name``, or else ``ninja.file_name`` in the context.
        
        :returns: Ninja file name
        :rtype: string
        """
        
        file_name = stringify(self._file_name)
        if file_name is None:
            file_name = stringify(self._project.file_name)
        if file_name is None:
            with current_context() as ctx:
                file_name = stringify(ctx.get('ninja.file_name', DEFAULT_NAME))
        if file_name is not None:
            file_name = u'%s.ninja' % file_name
        return file_name
    
    @file_name.setter
    def file_name(self, value):
        self._file_name = value
    
    @property
    def path(self):
        """
        Full path to the Ninja file. A join of the project's ``output_path`` and :attr:`file_name`. 
        
        :returns: full path to Ninja file
        :rtype: string
        """
        
        return join_path(self._project.output_path, self.file_name)

    @property
    def encoding(self):
        with current_context() as ctx:
            return ctx.fallback(self._encoding, 'ninja.encoding', DEFAULT_ENCODING)
    
    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    def generate(self):
        """
        Writes the Ninja file to :attr:`path`, overwriting existing contents and making sure to
        make parent directories.
        """
        
        output_path = self._project.output_path
        path = self.path
        announce(u"Generating '%s'" % path)
        if not os.path.isdir(output_path):
            makedirs(output_path)
        with io.open(path, 'w', encoding=self.encoding) as f:
            self.write(f)

    def remove(self):
        """
        Deletes the Ninja file at :attr:`path` if it exists.
        """
        
        path = self.path
        if os.path.isfile(path):
            os.remove(path)

    def build(self):
        """
        Calls :meth:`generate` and runs Ninja as a subprocess in build mode.
        
        :returns: subprocess exit code
        :rtype: integer
        """

        self.generate()
        path = self.path
        with current_context() as ctx:
            command = which(ctx.fallback(self.command, 'ninja.command', 'ninja'))
            verbose = ctx.get('cli.verbose', False)
        args = [command, '-f', path]
        if verbose:
            args.append('-v')
        try:
            check_call(args)
        except CalledProcessError as e:
            return e.returncode
        return 0

    def clean(self):
        """
        Runs Ninja as a subprocess in clean mode, and then deletes the Ninja file if successful.
        Also makes sure to clean any temporary state for the project in the context.
        
        :returns: subprocess exit code
        :rtype: integer
        """
        
        with current_context() as ctx:
            project_outputs = ctx.get('current.project_outputs')
            if project_outputs is not None:
                if self._project in project_outputs:
                    del project_outputs[self._project]
                
        path = self.path
        if os.path.isfile(path):
            with current_context() as ctx:
                command = which(ctx.fallback(self.command, 'ninja.command', 'ninja'))
            args = [command, '-f', path, '-t', 'clean', '-g']
            try:
                check_call(args)
            except CalledProcessError as e:
                return e.returncode
        self.remove()
        return 0

    def delegate(self):
        """
        Calls :meth:`build` and then exits the process with the correct exit code.
        """
        
        sys.exit(self.build())

    def write(self, f):
        """
        Writes the Nina file content.
        
        :param f: where to write
        :type f: file-like
        """
        
        with new_child_context() as ctx:
            columns = ctx.fallback(self.columns, 'ninja.file_columns', DEFAULT_COLUMNS)
            strict = ctx.fallback(self.strict, 'ninja.file_columns_strict', False)
            if strict and (columns is not None) and (columns < _MINIMUM_COLUMNS_STRICT):
                columns = _MINIMUM_COLUMNS_STRICT

            with _Writer(f, columns, strict) as w:
                ctx.current.writer = w
                ctx.current.phase_outputs = StrictDict(key_class=basestring, value_class=list)
                ctx.current.project = self._project
                ctx.current.project_outputs[self._project] = ctx.current.phase_outputs
                
                # Header
                w.comment(u'Ninja file for %s' % self._project)
                w.comment(u'Generated by Rōnin on %s' % datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))
                if columns is not None:
                    w.comment(u'Columns: %d (%s)' % (columns, 'strict' if strict else 'non-strict'))
                
                w.line()
                w.line(u'builddir = %s' % pathify(self._project.output_path))
                
                # Rules
                for phase_name, phase in self._project.phases.iteritems():
                    verify_type(phase, Phase)
                    self._write_rule(ctx, phase_name, phase)

    def _write_rule(self, ctx, phase_name, phase):
        phase_outputs = ctx.current.phase_outputs

        # Check if already written
        if phase_name in phase_outputs:
            return
        
        phase.apply()

        ctx.current.phase_name = phase_name
        ctx.current.phase = phase
        w = ctx.current.writer

        # From other phases
        inputs_from = self._get_phase_names(ctx, phase, 'inputs_from')
        rebuild_on_from = self._get_phase_names(ctx, phase, 'rebuild_on_from')
        build_if_from = self._get_phase_names(ctx, phase, 'build_if_from')
        
        # Rule
        rule_name = phase_name.replace(' ', '_')
        w.line()
        w.line(u'rule %s' % rule_name)
        
        # Description
        description = stringify(phase.description)
        if description is None:
            description = u'%s $out' % phase_name
        w.line(u'description = %s' % description, 1)

        # Command
        verify_type(phase.executor, Executor)
        command = phase.command_as_str(escape)
        w.line(u'command = %s' % command, 1)
        
        # Deps
        deps_file = stringify(phase.executor._deps_file)
        if deps_file:
            w.line(u'depfile = %s' % deps_file, 1)
            deps_type = stringify(phase.executor._deps_type)
            if deps_type:
                w.line(u'deps = %s' % deps_type, 1)

        # Implicit dependencies
        implicit_dependencies = phase.rebuild_on
        for n in rebuild_on_from:
            implicit_dependencies += [v.file for v in phase_outputs[n]]
        implicit_dependencies = dedup(implicit_dependencies)
        if implicit_dependencies:
            implicit_dependencies = u' | %s' % (' '.join(pathify(v) for v in implicit_dependencies))
        else:
            implicit_dependencies = u''

        # Order dependencies
        order_dependencies = phase.build_if
        for n in build_if_from:
            order_dependencies += [v.file for v in phase_outputs[n]]
        order_dependencies = dedup(order_dependencies)
        if order_dependencies:
            order_dependencies = u' || %s' % (' '.join(pathify(v) for v in order_dependencies))
        else:
            order_dependencies = u''
            
        # Inputs
        inputs = stringify_list(phase.inputs)
        for n in inputs_from:
            inputs += [v.file for v in phase_outputs[n]]
        inputs = dedup(inputs)
        
        # Outputs
        combine_inputs, outputs = phase.get_outputs(inputs)

        # Store outputs in state
        phase_outputs[phase_name] = outputs
        
        def build(output, inputs):
            line = u'build %s: %s' % (pathify(output.file), rule_name)
            if inputs:
                line += u' ' + u' '.join([pathify(v) for v in inputs])
            line += implicit_dependencies
            line += order_dependencies
            w.line(line)
            
            # Vars
            for var_name, var in phase.vars.iteritems():
                if hasattr(var, '__call__'):
                    var = var(output, inputs)
                w.line(u'%s = %s' % (var_name, var), 1)
    
        if combine_inputs:
            w.line()
            build(outputs[0], inputs)
        elif outputs:
            w.line()
            for index, output in enumerate(outputs):
                the_input = inputs[index]
                build(output, [the_input])

    def _get_phase_names(self, ctx, phase, attr):
        phase_names = []
        for value in getattr(phase, attr):
            if isinstance(value, Phase):
                p_name = self._project.get_phase_name(value)
                p = value
                if p_name is None:
                    raise ValueError(u'%s contains a phase that is not in the project' % attr)
            else:
                p_name = stringify(value)
                p = self._project.phases.get(p_name)
                if p is None:
                    raise ValueError(u'%s "%s" is not a phase in the project' % (attr, p_name))
            if p is phase:
                raise ValueError(u'%s contains self' % attr)

            phase_names.append(p_name)
            
            # Write this phase first, so we have results to collect
            self._write_rule(ctx, p_name, p)
            
        return phase_names

_MINIMUM_COLUMNS_STRICT = 30 # lesser than this can lead to breakage
_INDENT = '  '

class _Writer(object):
    def __init__(self, f, columns, strict):
        self._f = f
        self._columns = columns
        self._strict = strict

    def __enter__(self):
        return self
    
    def __exit__(self, the_type, value, traceback):
        pass
    
    def line(self, line='', indent=0):
        indentation = _INDENT * indent
        if self._columns is None:
            self._f.write(u'%s%s\n' % (indentation, line))
        else:
            leading_space_length = len(indentation)
            broken = False
                
            while leading_space_length + len(line) > self._columns:
                width = self._columns - leading_space_length - 2
                
                # First try: find last un-escaped space within width 
                space = width
                while True:
                    space = line.rfind(' ', 0, space)
                    if (space < 0) or _Writer._is_unescaped(line, space):
                        break                

                # Second try (if non-strict): find first un-escaped space after width
                if (space < 0) and (not self._strict):
                    space = width - 1
                    while True:
                        space = line.find(' ', space + 1)
                        if (space < 0) or _Writer._is_unescaped(line, space):
                            break

                if space != -1:
                    # Break at space
                    self._f.write(u'%s%s $\n' % (indentation, line[:space]))
                    line = line[space + 1:]
                    if not broken:
                        # Indent                               
                        broken = True
                        indentation += _INDENT
                        leading_space_length += len(_INDENT)
                elif self._strict:
                    # Break anywhere
                    width += 1
                    self._f.write(u'%s%s$\n' % (indentation, line[:width]))
                    line = line[width:]
                else:
                    break

            self._f.write(u'%s%s\n' % (indentation, line))

    def comment(self, line):
        if self._columns is None:
            self._f.write(u'# %s\n' % line)
        else:
            width = self._columns - 2
            lines = wrap(line, width, break_long_words=self._strict, break_on_hyphens=False)
            for line in lines:
                self._f.write(u'# %s\n' % line)

    @staticmethod        
    def _is_unescaped(line, i):
        dollar_count = 0
        dollar_index = i - 1
        while (dollar_index > 0) and (line[dollar_index] == '$'):
            dollar_count += 1
            dollar_index -= 1
        return dollar_count % 2 == 0
