#!/usr/bin/env python

#
# Rust Hello World
#
# build1.py
#
# Source: http://rustbyexample.com/hello.html
#
# Requirements:
#
#   Ubuntu: curl https://sh.rustup.rs -sSf | sh
#
# Rust comes with its own build system, Cargo, which is tightly integrated with the language.
# However, Ronin still provides basic Rust support, which can be useful in projects that combine
# Rust code with other languages.
#
# Note that if you want to easily use dependencies from crates.io, you will need to use Cargo.
# Unfortunately, Cargo cannot be used just to manage dependencies, so you will have to work
# entirely with Cargo.
#
# See build2.py for an example of integration with Cargo.
#

from ronin.cli import cli
from ronin.contexts import new_context
from ronin.phases import Phase
from ronin.projects import Project
from ronin.rust import RustBuild
from ronin.utils.paths import glob

with new_context(output_path_relative='build1') as ctx:

    project = Project('Rust Hello World')
    
    Phase(project=project,
          name='build',
          executor=RustBuild(),
          inputs=glob('src/hello1.rs'),
          output='hello1',
          run_output=1 if ctx.build.run else 0)
    
    cli(project)
