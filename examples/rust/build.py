#!/usr/bin/env python

#
# Rust Hello World
#
# build.py
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

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.phases import Phase
from ronin.projects import Project
from ronin.rust import RustBuild
from ronin.utils.paths import glob

with new_build_context() as ctx:

    project = Project('Rust Hello World')
    
    build = Phase(RustBuild(),
                  inputs=glob('src/**/*.rs'),
                  output='hello')

    project.phases['build'] = build
    
    cli(project)
