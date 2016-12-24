#!/usr/bin/env python

#
# Cross-compilation example
#
# build.py
#
# To test, try "--variant linux64" or "--variant linux32" when building.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_build_context() as ctx:
    project = Project('size')
    
    build = Phase(GccBuild(), output='size')
    build.command.set_machine_bits(project)
    build.inputs = glob('src/*.c')
    project.phases['build'] = build
    
    cli(project)
