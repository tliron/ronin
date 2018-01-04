#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# 浪人 gcc Unicode Example
#
# build.py
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache
#
# Rōnin supports Unicode.
#
# Note the magic "coding" comment at the top of this file, which tells Python to read the file in
# that encoding. Furthermore, in Python 2 we need to use the "u" prefix for literal strings that
# contain Unicode characters (unnecessary in Python 3).
#
# That's pretty much all you need to do: the Ninja file is created in UTF-8 by default.
# (To change its encoding, set "ninja.encoding" in the context.)
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_context() as ctx:
    
    project = Project(u'浪人 gcc Unicode Example')

    Phase(project=project,
          name='build', # Ninja limitation: phase names cannot be Unicode!
          executor=GccBuild(),
          inputs=glob(u'ソース/**/*.c'),
          output=u'長さ',
          run_output=1 if ctx.build.run else 0)

    cli(project)
