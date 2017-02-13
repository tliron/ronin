#!/usr/bin/env python

#
# gcc SDL Hello World
#
# build.py
#
# Source: https://github.com/Twinklebear/TwinklebearDev-Lessons/blob/master/Lesson1/src/main.cpp
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache libsdl2-dev
#
# Simple example of using SDL. Note that instead of using sdl_config.SDL() we could also have used
# pkg_config.Package('sdl2'). The difference is that sdl_config.SDL() uses the sdl2-config utility,
# which is more specialized than pkg-config.
#
# The script also supports linking SDL as a static library if you specify "--set sdl.static=true"
# in the command line.
#
# This is also an example of using the Copy executor. Note the use of the phase's
# "input_path_relative" in order to strip the input prefix. 
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.files import Copy
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.sdl import SDL
from ronin.utils.paths import glob

with new_context() as ctx:

    project = Project('gcc SDL Hello World')
    
    static = (ctx.get('sdl.static') == 'true')
    
    Phase(project=project,
          name='build',
          executor=GccBuild(),
          inputs=glob('src/**/*.c'),
          extensions=[SDL(static=static)],
          output='hello',
          run_output=1 if ctx.build.run else 0)

    Phase(project=project,
          name='resource',
          executor=Copy(),
          input_path_relative='res',
          inputs=glob('res/**'))
    
    cli(project)
