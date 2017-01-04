#!/usr/bin/env python

#
# Vala GTK+ Hello World
#
# build2.py
#
# Source: https://wiki.gnome.org/Projects/Vala/GTKSample
#
# Requirements:
#
#   Ubuntu: sudo apt install valac gcc libgtk-3-dev
#
# Here we're building a Vala program incrementally and in parallel. Unfortunately, valac does not
# make it easy for us, requiring four phases to be efficient. Luckily, Ronin automates a lot of it.
# It's recommended to take a look at the generated "build.ninja" just to see how complex it is.  
#
# The API phase generates ".vapi" files for each ".vala" file. This is required for the transpile
# phase, where we create a ".c" file for each ".vala" file, but we cannot do it in isolation and
# need to reference the ".vapi" files corresponding to each of the *other* ".vala" files. Got it? 
#
# The compile/link phases are more straightforward, though note that behind the scenes we are using
# pkg_config.Package to translate the Vala package into a library that gcc can use. In most cases
# the name of the Vala package is specifically made to be the same as what is used in
# pkg_config.Package, but we've seen quite a few exceptions. Check the documentation for
# ValaExtension to make sure you configure your packages correctly for four-phase builds.
#

from ronin.cli import cli
from ronin.contexts import new_build_context
from ronin.gcc import GccLink
from ronin.phases import Phase
from ronin.projects import Project
from ronin.vala import ValaApi, ValaTranspile, ValaGccCompile, ValaExtension
from ronin.utils.paths import glob

with new_build_context(output_path_relative='build2') as ctx:

    project = Project('Vala GTK+ Hello World')
    
    inputs = glob('src/**/*.vala')
    extensions = [ValaExtension('gtk+-3.0')]
    
    # API
    api = Phase(ValaApi(),
                inputs=inputs)
    api.executor.enable_deprecated()
    project.phases['api'] = api
    
    # Transpile
    transpile = Phase(ValaTranspile(apis=[api]),
                      inputs=inputs,
                      extensions=extensions)
    project.phases['transpile'] = transpile
 
    # Compile
    compile = Phase(ValaGccCompile(),
                    inputs_from=[transpile],
                    extensions=extensions)
    project.phases['compile'] = compile

    # Link
    link = Phase(GccLink(),
                 inputs_from=[compile],
                 extensions=extensions,
                 output='gtk-hello')
    project.phases['link'] = link
    
    cli(project)
