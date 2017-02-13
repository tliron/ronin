#!/usr/bin/env python

#
# gcc Cross-compilation Example
#
# build.py
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache gcc-multilib mingw-w64
#
# To test various builds, try "--variant linux64", "--variant linux32", "--variant win64",
# "--variant win32" in the command line. On Linux and OSX you can run the Windows builds using WINE.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_context() as ctx:
    
    project = Project('gcc Cross-compilation Example')

    Phase(project=project,
          name='build',
          executor=GccBuild(platform=project),
          inputs=glob('src/**/*.c'),
          output='size',
          run_output=1 if ctx.build.run else 0)

    cli(project)
