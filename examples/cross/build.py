#!/usr/bin/env python

#
# Cross-compilation example
#
# build.py
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccBuild
from ronin.projects import Project
from ronin.rules import Rule
from ronin.utils.paths import glob

with new_build_context() as ctx:

    p = Project('size')
    
    c = GccBuild()
    c.set_machine_bits(p)
    
    r = Rule(c)
    r.inputs = glob('src/*.c')
    r.output = 'size'
    
    p.rules['executable'] = r
    
    cli(p)
