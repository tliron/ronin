#!/usr/bin/env python

#
# Vala GTK+ Hello World
#
# build1.py
#
# Source: https://wiki.gnome.org/Projects/Vala/GTKSample
#
# Requirements:
#
#   Ubuntu: sudo apt install valac gcc libgtk-3-dev
#
# Building Vala (or Genie) programs seems simple, and it indeed *is* simple if you just do a
# one-phase build. Behind the scenes, valac transpiles your Vala (or Genie) code to C and invokes
# gcc as a single-phase build, adding all the correct compile and link arguments assigned to the
# Vala packages (implemented in Ronin as "ValaExtension").
#
# Unfortunately, this single-phase build style is very slow for large projects, and does not support
# incremental builds. See build2.py for a much more efficient way of using Ronin to build Vala
# programs.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.phases import Phase
from ronin.projects import Project
from ronin.vala import ValaBuild, ValaExtension
from ronin.utils.paths import glob

with new_build_context(output_path_relative='build1') as ctx:

    project = Project('Vala GTK+ Hello World')
    
    build = Phase(ValaBuild(),
                  inputs=glob('src/**/*.vala'),
                  extensions=[ValaExtension('gtk+-3.0')],
                  output='gtk-hello')

    project.phases['build'] = build
    
    cli(project)
