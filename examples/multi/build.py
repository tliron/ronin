#!/usr/bin/env python

#
# gcc Multi-Project Example
#
# build.py
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache
#
# Shows a single script building multiple projects: a shared library, plus an executable that uses
# that library.
#
# In this example we've given each project it's own Ninja file (using "file_name="). This is good
# enough to make sure each project builds separately while sharing the same build directory.
#
# However, note a potential pitfall in this strategy: in this situation it also means that both
# builds share the same ".ninja_deps" file, which is where Ninja keeps track of changed files.
# Because in this particular case the projects don't share source files, this is not a problem.
# However, to avoid conflicts it may be better to use "path=" instead of "file_name=" for each
# project, which would guarantee each project its own ".ninja_deps" file.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.gcc import GccBuild
from ronin.extensions import OutputsExtension
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob, input_path

with new_context() as ctx:

    # Library
    library = Project('gcc Multi-Project Example: Library', file_name='library')
    executor = GccBuild()
    executor.create_shared_library()
    executor.pic()
    Phase(project=library,
          name='build',
          executor=executor,
          inputs=glob('src/foo/**/*.c'),
          output='foo')
    
    # Main
    main = Project('Multi-Project Example: Main', file_name='main')
    executor = GccBuild()
    executor.add_include_path(input_path('src/foo'))
    executor.linker_rpath_origin() # to load the .so file from executable's directory
    Phase(project=main,
          name='build',
          executor=executor,
          inputs=glob('src/main/**/*.c'),
          extensions=[OutputsExtension(library, 'build')],
          output='main',
          run_output=1 if ctx.build.run else 0)
    
    cli(library, main)
