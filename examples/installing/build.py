#!/usr/bin/env python

#
# Installing Example
#
# build.py
#
# Requirements:
#
#   Ubuntu: sudo apt install gcc ccache
#
# To install your build, use the Copy executor and set "inputs_from=" to the generating phase,
# as well as "output_strip_prefix_from=" if you want to strip the original output path. 
#
# Run with the "--install" CLI argument to enable "build.install" in the context. In this example
# we're using "paths.install" in the context to override a safe default install path, so a complete
# install command would look something like this:
#
#  ./build.py --install --set paths.install=/usr/bin
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.files import Copy
from ronin.gcc import GccBuild
from ronin.phases import Phase
from ronin.projects import Project
from ronin.utils.paths import glob, join_path

with new_context() as ctx:
    
    project = Project('Installing Example')

    install_path = ctx.get('paths.install', join_path(ctx.paths.root, 'install'))

    Phase(project=project,
          name='build',
          executor=GccBuild(),
          inputs=glob('src/**/*.c'),
          output='size',
          run_output=1 if ctx.build.run else 0)

    if ctx.build.install:
        Phase(project=project,
              name='install',
              executor=Copy(),
              inputs_from=['build'],
              output_strip_prefix_from='build',
              output_path=install_path)

    cli(project)
