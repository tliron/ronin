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
# This adds on build1.py by separating the compile and link phases. 
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccCompile, GccLink
from ronin.pkg_config import Package
from ronin.projects import Project
from ronin.rules import Rule
from ronin.utils.paths import glob

with new_build_context() as ctx:
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
    c.add_libraries(*libraries)
    
    r = Rule(c)
    r.source = 'object'
    r.output = 'example_1'
    p.rules['executable'] = r
    
    cli(p)
