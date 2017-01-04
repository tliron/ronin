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
# "--variant win32" in the command line. On Linux you can run the Windows builds using WINE.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_build_context() as ctx:
    
    project = Project('gcc Cross-compilation Example')
    build = Phase(GccBuild(platform=project),
                  inputs=glob('src/*.c'),
                  output='size')
    project.phases['build'] = build
    cli(project)
