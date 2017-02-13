#!/usr/bin/env python

#
# g++ Qt Hello World
#
# build.py
#
# Source: https://wiki.qt.io/Qt_for_Beginners
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache libqt4-dev
#
# Qt is an especially comprehensive framework, and even includes its own build tool, qmake, which
# in turn uses Make. And even an IDE, Qt Creator, which can use CMake (instead of qmake), which
# supports Ninja. But, we want Ronin!
#
# You can write Qt programs in pure C++. However, Qt code often includes special macros that are
# used by a preprocessor (the meta-object compiler, "moc") to inject boilerplate code. Thus,
# you will also need a QtMetaObjectCompile phase.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.pkg_config import Package
from ronin.projects import Project
from ronin.qt import QtMetaObjectCompile
from ronin.utils.paths import glob

with new_context() as ctx:

    project = Project('g++ Qt Hello World')
    
    Phase(project=project,
          name='meta',
          executor=QtMetaObjectCompile(),
          inputs=glob('src/**/*.h'))
    
    Phase(project=project,
          name='build',
          executor=GccBuild('g++'),
          inputs=glob('src/**/*.cpp'),
          inputs_from=['meta'],
          extensions=[Package('QtGui')],
          output='hello',
          run_output=1 if ctx.build.run else 0)

    cli(project)
