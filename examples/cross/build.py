#!/usr/bin/env python

#
# Cross-compilation example
#
# build.py
#
# Requirements: sudo apt install gcc ccache gcc-multilib mingw-w64
#
# To test, try "--variant linux64", "--variant linux32", "--variant win64", "--variant win32".
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_build_context() as ctx:
    project = Project('size')
    build = Phase(GccBuild(crosscompile=project), inputs=glob('src/*.c'), output='size')
    project.phases['build'] = build
    cli(project)
