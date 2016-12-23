Ronin
=====

A straightforward but powerful build system based on [Ninja](https://ninja-build.org/) and Python.

"Based on Python" means that not only is it written in Python, but also it uses Python as the DSL
for build scripts. Many build systems invent their own DSLs, but Ronin intentionally builds on a
language that already exists. Note that you _don't_ need to be an expert in Python to use Ronin,
but the power is there if you need it.

Goals:

1. **Easy to use**: _optional_ auto-configuration with sensible, _overridable_ defaults: detect
   `ccache`, support `pkg-config`, etc.
2. **Complex does not have to mean complicated**: handle cross-compilations and other
   multi-configuration builds as single projects with minimal duplication of effort.

The design principles:

1. Pour some sugar on me: make common tasks easier with sweet and coherent helper. But make sure
   that sugar is optional, allowing the script to be more verbose if it's helpful. 
2. Don't hide functionality behind complexity: for example, if the user wants to manipulate a
   compiler command line, let them do it easily. Too many build systems bungle this and make it
   either impossible or very difficult to do something that would be trivial using a shell script.
3. Don't reinvent wheels: if Python or Ninja do something for us, use it. The build script is a
   plain Python program with no unnecessary cleverness. The generated Ninja script looks like
   something you could have created manually.

Similar Projects
----------------

* [Meson](http://mesonbuild.com/): another Python frontend for Ninja, very high-level, fairly easy
  to use
* [Craftr](https://github.com/craftr-build/craftr): another Python frontend for Ninja, more
  low-level than Meson, but also more complicated to use 
* [CMake](https://cmake.org/): can work as a frontend for Ninja
* [Waf](https://waf.io/): a big Python build system (and platform for build systems)
