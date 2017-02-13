#!/usr/bin/env python

#
# Java Swing Hello World
#
# build.py
#
# Source: http://www.java2s.com/Code/Java/Swing-JFC/HelloWorldSwing.htm
#
# Requirements:
#
#   Ubuntu: sudo apt install openjdk-8-jdk
#
# Though javac does not care about the directory structure of the source ".java" files, it emits
# compiled ".class" files in a directory hierarchy matching the package structure. For Ninja to be
# able to properly track source changes, make sure your source files are also in a directory
# hierarchy that matches the package structure, and also set "input_path=".
#
# The jar command is similarly finicky about paths, however the JavaClasses extension will make sure
# to do the right thing. Take a look at the generated "build.ninja" for details.
#
# This is also a nice example of using "run_command=" in order to run our output Jar.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.java import JavaCompile, Jar, JavaClasses
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob, input_path, join_path
from ronin.utils.platform import which

with new_context() as ctx:

    project = Project('Java Swing Hello World')
    
    # Compile
    Phase(project=project,
          name='compile',
          executor=JavaCompile(),
          input_path=join_path(ctx.paths.root, 'src'),
          inputs=glob('**/*.java'))
    
    # Jar
    Phase(project=project,
          name='jar',
          executor=Jar(manifest=input_path('MANIFEST.MF')),
          extensions=[JavaClasses(project, 'compile')],
          output='hello',
          run_output=1 if ctx.build.run else 0,
          run_command=[which('java'), '-jar', '{output}'])
    
    cli(project)
