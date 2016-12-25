#!/usr/bin/env python

#
# GTK+ Hello World
#
# build2.py
#
# Source: https://developer.gnome.org/gtk3/stable/gtk-getting-started.html
#
# Requirements: sudo apt install gcc ccache libgtk-3-dev
#
# This adds on build1.py by separating the compile and link phases.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccCompile, GccLink
from ronin.phases import Phase
from ronin.pkg_config import Package
from ronin.projects import Project
from ronin.utils.paths import glob

with new_build_context() as ctx:
    project = Project('GTK+ Hello World')
    libraries = [Package('gtk+-3.0')]
    
    # Compile
    compile = Phase(GccCompile(), inputs=glob('src/*.c'))
    compile.command.libraries += libraries
    project.phases['compile'] = compile

    # Link
    link = Phase(GccLink(), inputs_from=[compile], output='example_1')
    link.command.libraries += libraries
    project.phases['link'] = link
    
    cli(project)
