#!/usr/bin/env python

#
# g++ SDL Hello World
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

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.files import Copy
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.sdl_config import SDL
from ronin.utils.paths import glob

with new_build_context() as ctx:

    project = Project('g++ SDL Hello World')
    
    static = (ctx.sdl.static == 'true')
    
    build = Phase(GccBuild('g++'),
                  inputs=glob('src/*.cpp'),
                  extensions=[SDL(static=static)],
                  output='hello')
    build.executor.standard('c++0x')

    resource = Phase(Copy(),
                     inputs=glob('res/*'))

    project.phases['build'] = build
    project.phases['resource'] = resource
    
    cli(project)
