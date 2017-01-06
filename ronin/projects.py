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
from collections import OrderedDict

class Project(object):
    """
    An interrelated set of build phases.
    """
    
    def __init__(self, name, path=None, file_name=None, version=None, variant=None, phases=None):
        self.name = name
        self.path = path
        self.file_name = file_name
        self.version = version
        self.phases = phases or OrderedDict()
        self.hooks = []
        self._variant = variant or (lambda ctx: ctx.get('projects.default_variant', host_platform()))

    def __str__(self):
        name = stringify(self.name)
        version = stringify(self.version)
        variant = stringify(self.variant)
        if version and variant:
            return '%s %s (%s)' % (name, version, variant)
        elif version and not variant:
            return '%s %s' % (name, version)
        elif variant and not version:
            return '%s (%s)' % (name, variant)
        else:
            return name

    @property
    def variant(self):
        return stringify(self._variant)
    
    @property
    def is_windows(self):
        return self.variant in ('win64', 'win32')

    @property
    def is_linux(self):
        return self.variant in ('linux64', 'linux32')

    @property
    def executable_extension(self):
        return platform_executable_extension(self.variant)
    
    @property
    def shared_library_extension(self):
        return platform_shared_library_extension(self.variant)

    @property
    def shared_library_prefix(self):
        return platform_shared_library_prefix(self.variant)
    
    @property
    def output_path(self):
        with current_context() as ctx:
            return join_path(ctx.paths.output, self.path, self.variant)

    def get_output_path(self, output_type):
        with current_context() as ctx:
            output_path = ctx.get('paths.%s' % output_type)
        if output_path is None:
            output_path = join_path(self.output_path, ctx.get('paths.%s_relative' % output_type))
        return output_path

    def get_phase_name(self, phase):
        for k, v in self.phases.iteritems():
            if v is phase:
                return k
        return None
