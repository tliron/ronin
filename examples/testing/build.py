#!/usr/bin/env python

#
# Testing with Check
#
# build.py
#
# Source: https://libcheck.github.io/check/doc/check_html/check_3.html
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache check
#
# In this example we'll see how to integrate the popular Check unit testing framework for C.
#
# Notes:
#
# 1) We'll only build/run the tests if run with "build.py test".
# 2) We're putting the test sources and binary outputs in separate folders. This is a common
#    practice that keeps things clean.
# 3) Because our program already has a "main" function, we're linking it separately as a shared
#    library so that we can use a different "main" function that runs the tests. If you're testing
#    a library, you obviously don't need this separate step.
# 4) We're setting integer values to "run_input=" in order to make sure that tests run before
#    the program.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.gcc import GccCompile, GccLink, GccBuild
from ronin.phases import Phase
from ronin.pkg_config import Package
from ronin.projects import Project
from ronin.utils.paths import glob, join_path

with new_context() as ctx:

    project = Project('Testing with Check')
    
    # Compile
    Phase(project=project,
          name='compile',
          executor=GccCompile(),
          inputs=glob('src/**/*.c'))
    project.phases['compile'].executor.pic()

    # Link program
    Phase(project=project,
          name='link_program',
          executor=GccLink(),
          inputs_from=['compile'],
          output='money',
          run_output=2 if ctx.build.run else 0)

    if ctx.build.test:
        tests_path = join_path(project.get_output_path('binary'), 'tests')
        
        # Link library
        Phase(project=project,
              name='link_library',
              executor=GccLink(),
              inputs_from=['compile'],
              output_path=tests_path,
              output='money')
        project.phases['link_library'].executor.create_shared_library()
        
        # Tests
        Phase(project=project,
              name='tests',
              executor=GccBuild(),
              inputs=glob('tests/**/*.c'),
              inputs_from=['link_library'],
              extensions=[Package('check')],
              output_path=tests_path,
              output='tests',
              run_output=1)
        project.phases['tests'].executor.enable_threads() # required by Check
    
    cli(project)
