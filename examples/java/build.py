#!/usr/bin/env python

#
# Java Hello World
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
# The jar command is similarly finicky about paths, however the ClassesExtension will make sure
# to do the right thing. Take a look at the generated "build.ninja" for details. 
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.java import JavaCompile, Jar, ClassesExtension
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob, input_path, join_path

with new_context() as ctx:

    project = Project('Java Hello World')
    
    # Compile
    compile = Phase(JavaCompile(),
                    input_path=join_path(ctx.paths.root, 'src'),
                    inputs=glob('**/*.java'))
    project.phases['compile'] = compile
    
    # Jar
    jar = Phase(Jar(manifest=input_path('MANIFEST.MF')),
                extensions=[ClassesExtension(project, 'compile')],
                output='hello')
    project.phases['jar'] = jar
    
    cli(project)
