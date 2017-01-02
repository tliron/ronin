#!/usr/bin/env python

#
# Multi-Project Example
#
# build.py
#
# Requirements: sudo apt install gcc ccache
#
# Shows a single script building multiple projects: a shared library, plus an executable that uses
# that library.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.extensions import OutputsExtension
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob, input_path

with new_build_context() as ctx:
    # Extension
    library = Project('Multi-Project Example: Extension', file_name='library')
    build_library = Phase(GccBuild(),
                          inputs=glob('src/foo/*.c'),
                          output='foo')
    build_library.executor.create_shared_library()
    build_library.executor.pic()
    library.phases['build'] = build_library
    
    # Main
    main = Project('Multi-Project Example: Main', file_name='main')
    build_main = Phase(GccBuild(),
                       inputs=glob('src/main/*.c'),
                       extensions=[OutputsExtension(library, 'build')],
                       output='main')
    build_main.executor.add_include_path(input_path('src/foo'))
    build_main.executor.linker_rpath_origin() # to load the .so file from executable's directory
    main.phases['build'] = build_main
    
    cli(library, main)
