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

from .contexts import current_context
from .utils.platform import host_platform, platform_executable_extension, platform_shared_library_extension, platform_shared_library_prefix
from .utils.strings import stringify
from .utils.paths import join_path
from .utils.collections import StrictDict, StrictList

class Project(object):
    """
    A container for an interrelated set of build phase (see :class:`ronin.phases.Phase`).
    
    Every project is equivalent to a single Ninja file. Projects by default inherit properties from
    the current context, but can override any of them.
    
    A Rōnin build script can in turn consist of any number of projects, though likely would require
    at least one to do something useful. Actually, due the dynamic nature of Rōnin build scripts, an
    entirely different number and nature of projects may be created by each run of a script.
    
    After setting up projects, they are usually handed over to :func:`ronin.cli.cli`. Though, you
    can also use the :class:`ronin.ninja.NinjaFile` class directly instead.
    
    :ivar phases: phases
    :vartype phases: {string, :class:`ronin.phases.Phase`}
    :ivar hooks: called when generating the Ninja file
    :vartype hooks: [function]
    """
    
    def __init__(self,
                 name,
                 version=None,
                 variant=None,
                 input_path=None,
                 input_path_relative=None,
                 output_path=None,
                 output_path_relative=None,
                 file_name=None,
                 phases=None):
        """
        :param name: project name
        :type name: string|function
        :param version: project version
        :type version: string|function
        :param variant: override project variant; defaults to the context's ``project.default_variant``
                        or :func:`ronin.utils.platform.host_platform`
        :type variant: string|function
        :param input_path: override input path; defaults to the context's ``paths.input_path``
        :type input_path: string|function
        :param input_path_relative: override input path (relative)
        :type input_path_relative: string|function
        :param output_path: override output path generation
        :type output_path: string|function
        :param output_path_relative: override output path generation (relative)
        :type output_path_relative: string|function
        :param file_name: override Ninja file name; defaults to the context's ``ninja.file_name``
        :type file_name: string|function
        :param phases: project phases
        :type phases: {string, :class:`ronin.phases.Phase`}
        """
        
        self.name = name
        self.version = version
        self.input_path = input_path
        self.input_path_relative = input_path_relative
        self.output_path = output_path
        self.output_path_relative = output_path_relative
        self.file_name = file_name
        self.phases = phases or StrictDict(key_class=basestring, value_class='ronin.phases.Phase')
        self.hooks = StrictList(value_class='types.FunctionType')
        self._variant = variant or (lambda ctx: ctx.get('projects.default_variant', host_platform()))

    def __unicode__(self):
        name = stringify(self.name)
        version = stringify(self.version)
        variant = stringify(self.variant)
        if version and variant:
            return u'%s %s (%s)' % (name, version, variant)
        elif version and not variant:
            return u'%s %s' % (name, version)
        elif variant and not version:
            return u'%s (%s)' % (name, variant)
        else:
            return name

    @property
    def variant(self):
        """
        Project variant.
        
        :rtype: string
        """
        
        return stringify(self._variant)
    
    @property
    def is_windows(self):
        """
        True if :attr:`variant` is a Windows platform.
        
        :rtype: boolean
        """

        return self.variant in ('win64', 'win32')

    @property
    def is_linux(self):
        """
        True if :attr:`variant` is a Linux platform.
        
        :rtype: boolean
        """

        return self.variant in ('linux64', 'linux32')

    @property
    def executable_extension(self):
        """
        The executable extension for the :attr:`variant`.
        
        See: :func:`ronin.utils.platform.platform_executable_extension`.
        
        :rtype: string
        """
        
        return platform_executable_extension(self.variant)
    
    @property
    def shared_library_extension(self):
        """
        The shared library extension for the :attr:`variant`.
        
        See: :func:`ronin.utils.platform.platform_shared_library_extension`.
        
        :rtype: string
        """

        return platform_shared_library_extension(self.variant)

    @property
    def shared_library_prefix(self):
        """
        The shared library prefix for the :attr:`variant`.
        
        See: :func:`ronin.utils.platform.platform_shared_library_prefix`.
        
        :rtype: string
        """

        return platform_shared_library_prefix(self.variant)

    @property
    def input_path(self):
        """
        The set ``input_path``, or the context's ``paths.input``.
        
        :returns: input path
        :rtype: string 
        """
        
        input_path = stringify(self._input_path)
        if input_path is None:
            with current_context() as ctx:
                input_path = join_path(ctx.paths.input, self.input_path_relative)
        return input_path

    @input_path.setter
    def input_path(self, value):
        self._input_path = value

    @property
    def output_path(self):
        """
        The set ``output_path``, or the context's ``paths.output`` joined to the project's
        ``output_path_relative`` and :attr:`variant`.
        
        :returns: output path
        :rtype: string 
        """
        
        output_path = stringify(self._output_path)
        if output_path is None:
            with current_context() as ctx:
                output_path = join_path(ctx.paths.output, self.output_path_relative, self.variant)
        return output_path

    @output_path.setter
    def output_path(self, value):
        self._output_path = value

    def get_output_path(self, output_type):
        """
        The context's ``paths.[output_type]`` or project's :attr:`output_path` joined to the
        context's ``paths.[output_type]_relative``.
        
        :param output_type: output type
        :type output_type: string|function
        :returns: output path for output the type
        :rtype: string 
        """

        output_type = stringify(output_type)
        with current_context() as ctx:
            output_path = ctx.get('paths.%s' % output_type)
        if output_path is None:
            output_path = join_path(self.output_path, ctx.get('paths.%s_relative' % output_type))
        return output_path

    def get_phase_name(self, phase):
        """
        The name of the phase if it's in the project.
        
        :param phase: phase
        :type phase: :class:`ronin.phases.Phase`
        :returns: phase name or None
        :rtype: string
        """
        
        for k, v in self.phases.iteritems():
            if v is phase:
                return k
        return None
