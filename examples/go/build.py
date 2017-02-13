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
    Phase(project=project,
          name='compile_main',
          executor=GoCompile(),
          inputs=glob('src/main.go'),
          extensions=extensions,
          output='main')

    # Compile functions
    Phase(project=project,
          name='compile_functions',
          executor=GoCompile(),
          inputs=glob('src/functions.go'),
          output='ronin/functions')

    # Link
    Phase(project=project,
          name='link',
          executor=GoLink(),
          inputs_from=['compile_main'],
          extensions=extensions,
          output='example',
          run_output=1 if ctx.build.run else 0)
    
    cli(project)
