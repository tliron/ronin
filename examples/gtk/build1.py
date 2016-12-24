#!/usr/bin/env python

#
# GTK+ Hello World
#
# build1.py
#
# Source: https://developer.gnome.org/gtk3/stable/gtk-getting-started.html
#
# Requirements: sudo apt install libgtk-3-dev
#
# This is the simplest possible version, using all the sensible defaults.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.pkg_config import Package
from ronin.projects import Project
from ronin.utils.paths import glob

with new_build_context() as ctx:
    project = Project('GTK+ Hello World')
    
    build = Phase(GccBuild(), inputs=glob('src/*.c'), output='example_1')
    build.command.add_libraries(Package('gtk+-3.0'))
    project.phases['executable'] = build
    
    cli(project)
