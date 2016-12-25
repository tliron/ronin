#!/usr/bin/env python

#
# Multi-Project Example
#
# build.py
#
# Requirements: sudo apt install gcc ccache
#
# Shows a single script building multiple projects: a shared library, plus an executable that
# uses that library.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.libraries import ResultsLibrary
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob, input_path

with new_build_context() as ctx:
    library = Project('Multi-Project: Library', file_name='library')
    build_library = Phase(GccBuild(), inputs=glob('src/foo/*.c'), output='libfoo')
    build_library.command.create_shared_library()
    library.phases['build'] = build_library
    
    main = Project('Multi-Project: Main', file_name='main')
    build_main = Phase(GccBuild(), inputs=glob('src/main/*.c'), output='main')
    build_main.command.add_include_path(input_path('src/foo'))
    build_main.command.libraries.append(ResultsLibrary(build_library))
    build_main.command.rpath_origin() # allows loading the .so file from executable's directory
    main.phases['build'] = build_main
    
    cli(library, main)
