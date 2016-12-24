#!/usr/bin/env python

#
# GTK+ Hello World
#
# build2.py
#
# Source: https://developer.gnome.org/gtk3/stable/gtk-getting-started.html
#
# Requirements: sudo apt install libgtk-3-dev
#
# This adds on build2.py by explicit configuring the utilities. 
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import configure_gcc, GccCompile, GccLink
from ronin.pkg_config import configure_pkg_config, Package
from ronin.projects import Project
from ronin.ninja import configure_ninja
from ronin.rules import Rule
from ronin.utils.paths import base_path, glob

with new_build_context(root_path=base_path(__file__),
                       output_path_relative='build',
                       binary_path_relative='bin',
                       object_path_relative='obj',
                       debug=True) as ctx:

    configure_ninja(ctx,
                    command='ninja',
                    file_name='build.ninja',
                    columns=100)
    configure_gcc(ctx,
                  command='gcc',
                  ccache=True)
    configure_pkg_config(ctx,
                         command='pkg-config',
                         path=None)

    p = Project('example_1')

    libraries = [Package('gtk+-3.0')]
    
    # Compile
    
    c = GccCompile()
    c.add_libraries(*libraries)
    
    r = Rule(c)
    r.inputs = glob('src/*.c')
    p.rules['object'] = r

    # Link
    
    c = GccLink()
    c.set_machine_bits(p)
    c.add_libraries(*libraries)
    
    r = Rule(c)
    r.source = 'object'
    r.output = 'example_1'
    p.rules['executable'] = r
    
    cli(p)

