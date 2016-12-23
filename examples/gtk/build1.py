#!/usr/bin/env python

#
# GTK+ Hello World
#
# build1.py
#
# Source: https://developer.gnome.org/gtk3/stable/gtk-getting-started.html
#
# This is the simplest possible version, using all the sensible defaults.
#

from ronin import configure_build
from ronin.cli import build_cli
from ronin.contexts import new_context
from ronin.gcc import GccBuild
from ronin.pkg_config import Package
from ronin.projects import Project
from ronin.rules import Rule
from ronin.utils import base_path, glob

with new_context() as ctx:
    configure_build(ctx, base_path(__file__))

    p = Project('example_1')
    
    c = GccBuild()
    c.add_libraries(Package('gtk+-3.0'))
    
    r = Rule(c)
    r.inputs = glob('*.c')
    r.output = 'example_1'
    
    p.rules['executable'] = r
    
    build_cli(p)
