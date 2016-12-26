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
# This adds on build2.py by explicit configuring the utilities and adding verbosity.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import configure_gcc, GccCompile, GccLink
from ronin.phases import Phase
from ronin.pkg_config import configure_pkg_config, Package
from ronin.projects import Project
from ronin.ninja import configure_ninja
from ronin.utils.paths import base_path, glob

with new_build_context(root_path=base_path(__file__),
                       input_path_relative=None,
                       output_path_relative='build',
                       binary_path_relative='bin',
                       object_path_relative='obj') as ctx:

    configure_ninja(command='ninja',
                    file_name='build.ninja',
                    columns=100,
                    strict=False)
    
    configure_gcc(command='gcc',
                  ccache=True,
                  ccache_path='/usr/lib/ccache')
    
    configure_pkg_config(command='pkg-config',
                         path=None)

    project = Project('GTK+ Hello World')
    extensions = [Package('gtk+-3.0')]
    
    # Compile
    compile = Phase()
    compile.executor = GccCompile()
    compile.inputs = glob('src/*.c')
    compile.extensions += extensions

    # Link
    link = Phase()
    link.executor = GccLink()
    link.inputs_from.append('compile')
    link.extensions += extensions
    link.output = 'example_1'

    project.phases['compile'] = compile
    project.phases['link'] = link
    
    cli(project)
