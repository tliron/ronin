#!/usr/bin/env python

#
# GTK+ Hello World
#
# build2.py
#
# Source: https://developer.gnome.org/gtk3/stable/gtk-getting-started.html
#
# This improves on build1.py by adding explicit configuration of all utilities. 
#

from ronin import configure_build
from ronin.cli import build_cli
from ronin.contexts import new_context
from ronin.gcc import configure_gcc, GccBuild
from ronin.pkg_config import configure_pkg_config, Package
from ronin.projects import Project
from ronin.ninja import configure_ninja
from ronin.rules import Rule
from ronin.utils import base_path, glob

with new_context() as ctx:
    configure_build(ctx,
                    base_path(__file__),
                    output_path_relative='build',
                    binary_path_relative='bin',
                    debug=True)
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
    
    c = GccBuild()
    c.add_libraries(Package('gtk+-3.0'))
    
    r = Rule(c)
    r.inputs = glob('*.c')
    r.output = 'example_1'
    
    p.rules['executable'] = r
    
    build_cli(p)
