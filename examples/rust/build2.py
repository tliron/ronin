#!/usr/bin/env python

#
# Rust GTK+ Hello World
#
# build2.py
#
# Source: https://github.com/gtk-rs/examples
#
# Requirements:
#
#   Ubuntu: curl https://sh.rustup.rs -sSf | sh
#
# Here we show how to use a Cargo.toml file via Ronin. Cargo has its own rather rigid directory
# structure, so expect all output files under the "target" directory (instead of Ronin's "build2" in
# this case).
#
# Cargo will be doing all the heavy lifting. You just want to make sure that Ninja knows when to
# rebuild, so set "output=" to equal your "[[bin]]" definition in Cargo.toml, and use
# "rebuild_on=" with the relevant source files.
#
# This example doesn't really make much use of Ronin, but shows how you can still integrate Cargo
# into a Ronin build script.
#
# Note that the first build will take a minute or two, because Cargo will download and build the
# GTK+ library and its many dependencies. Be patient. You can see them later in
# "target/[release/debug]/deps".
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.phases import Phase
from ronin.projects import Project
from ronin.rust import CargoBuild
from ronin.utils.paths import input_path, glob

with new_context(output_path_relative='build2') as ctx:

    project = Project('Rust GTK+ Hello World')
    
    Phase(project=project,
          name='build',
          executor=CargoBuild(),
          inputs=[input_path('Cargo.toml')],
          rebuild_on=glob('src/hello2.rs'),
          output='hello2',
          run_output=1 if ctx.build.run else 0)
    
    cli(project)
