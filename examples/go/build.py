#!/usr/bin/env python

#
# Go Example
#
# build.py
#
# Source: https://gobyexample.com/functions
#
# Requirements:
#
#   Ubuntu: sudo apt install golang-go
#
# Go supports classic two-phase builds, but there are two caveats:
#
# If your Go program compromises several packages, then you need a separate compile phase for each
# package. If the package comprises several files, they need to be combined into a single "output="
# in the phase. Its value should be the same path you want to use for "import" in Go. This means
# that your source directory structure does not matter. Then, use the GoPackage extension on phases
# that import that package to ensure proper build order and import paths.
#
# Also, note that the link phase accepts only *one* input, which is the "main" package. The linker
# will automatically link imported packages. However, it again needs the GoPackage extension in
# order to ensure proper build order and import paths.
#
# Take a look at the generated "build.ninja" for details.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.go import GoCompile, GoLink, GoPackage
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob

with new_context() as ctx:

    project = Project('Go Example')
    
    extensions = [GoPackage(project, 'compile_functions')]
    
    # Compile main
    compile_main = Phase(GoCompile(),
                         inputs=glob('src/main.go'),
                         extensions=extensions,
                         output='main')
    project.phases['compile_main'] = compile_main

    # Compile functions
    compile_functions = Phase(GoCompile(),
                              inputs=glob('src/functions.go'),
                              output='ronin/functions')
    project.phases['compile_functions'] = compile_functions

    # Link
    link = Phase(GoLink(),
                 inputs_from=[compile_main],
                 extensions=extensions,
                 output='example')
    project.phases['link'] = link
    
    cli(project)
