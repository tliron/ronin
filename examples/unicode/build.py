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
# that encoding. Furthermore, in Python 2 we need to import "unicode_literals" so that our literal
# strings be of type "unicode" rather than "str" (unnecessary in Python 3).
#
# That's pretty much all you need to do: Ronin creates the Ninja file in UTF-8 by default. (To
# change the encoding, set "ninja.encoding" in the context.)
#

from __future__ import unicode_literals
from ronin.cli import cli
from ronin.contexts import new_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_context() as ctx:
    
    project = Project('浪人 gcc Unicode Example')

    Phase(project=project,
          name='build',
          executor=GccBuild(),
          inputs=glob('ソース/**/*.c'),
          output='長さ',
          run_output=1 if ctx.build.run else 0)

    cli(project)
