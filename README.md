Rōnin
=====

A straightforward but powerful build system based on [Ninja](https://ninja-build.org/) and
[Python](https://www.python.org/), suitable for projects both big and small.

Rōnin comes in [frustration-free packaging](https://en.wikipedia.org/wiki/Wrap_rage). Let's build
all the things!

Features
--------

Currently supported out-of-the-box:
all [gcc](https://gcc.gnu.org/) languages,
[Java](https://www.oracle.com/java/),
[Rust](https://www.rust-lang.org/),
[Go](https://golang.org/),
[Vala](https://wiki.gnome.org/Projects/Vala)/[Genie](https://wiki.gnome.org/Projects/Genie),
[pkg-config](https://www.freedesktop.org/wiki/Software/pkg-config/),
[Qt tools](https://www.qt.io/),
[sdl2-config](https://wiki.libsdl.org/Installation), and
[binutils](https://sourceware.org/binutils/docs/binutils/).

It's also easy to integrate your favorite
[testing framework](https://github.com/tliron/ronin/wiki/Testing%20and%20Running).

"Based on Python" means that not only is it written in Python, but also it uses
**Python as the DSL** for build scripts. Many build systems invent their own DSLs, but Rōnin
intentionally uses a language that already exists. There's no hidden cost to this design choice:
build scripts are pretty much as concise and coherent as any specialized DSL. You _don't_ need to be
an expert in Python to use Rōnin, but its power is at your fingertips if you need it.

Rōnin supports **Unicode** throughout: Ninja files are created in UTF-8 by default and you can
include Unicode characters in your build scripts.

Download
--------

Available on [PyPI](https://pypi.python.org/pypi/ronin), so you can install with `pip`,
`easy_install`, or `setuptools`. On Debian/Ubuntu: 

	sudo apt install python-setuptools
	sudo -H easy_install pip
	sudo -H pip2 install ronin

Since Ninja is just one small self-contained executable, it's easy to get it by downloading the
[latest release](https://github.com/ninja-build/ninja/releases). Just make sure it's in your
execution path, or run your build script with `--set ninja.command=` and give it the full path to
`ninja`. Older versions (they work fine) are also available on Debian/Ubuntu:

	sudo apt install ninja-build 

Documentation
-------------

An undocumented system is a broken system. We strive for coherent, comprehensive, and up-to-date
documentation.

A detailed user manual is available on the [wiki](https://github.com/tliron/ronin/wiki).

Rich API docs available on [Read the Docs](http://ronin.readthedocs.io/en/latest/).

Feelings
-------- 

Guiding lights:

1. **Powerful does not have to mean hard to use**: _optional_ auto-configuration with sensible,
   _overridable_ defaults.
2. **Complex does not have to mean complicated**: handle cross-compilation and other
   multi-configuration builds in a single script with minimal duplication of effort.

Design principles:

1. **Don't hide functionality behind complexity**: the architecture should be straightforward. For
   example, if the user wants to manipulate a compiler command line, let them do it easily. Too many
   build systems bungle this and make it either impossible or very difficult to do something that
   would be trivial using a shell script.
2. **Pour some sugar on me**: make common tasks easier with sweet utility functions. But make sure
   that sugar is optional, allowing the script to be more verbose when more control is necessary. 
3. **Don't reinvent wheels**: if Python or Ninja do something for us, use it. The build script is a
   plain Python program without any unnecessary cleverness. The generated Ninja file looks like
   something you could have created manually.

FAQ
---

* _Do we really need another build system?_ Yes. The other existing ones have convoluted
  architectures, impossible to opt-out-from automatic features, or are otherwise hostile to
  straightforward hacking. After so much wasted time fighting build systems to make them work for
  us, the time came to roll out a new one that does it right.
* _Python is too hard. Why not create a simpler DSL?_ Others have done it, and it seems that the
  costs outweigh the benefits. Making a new language is not trivial. Making a _robust_ language
  could take years of effort. Python is here right now, with a huge ecosystem of libraries and
  tools. Yes, it introduces a learning curve, but getting familiar with Python is useful for so
  many practical reasons beyond writing build scripts for Rōnin. That said, if someone wants to
  contribute a simple DSL as an optional extra, we will consider!
* _Why require Ninja, a binary, instead of building everything in 100% Python?_ Because it's silly
  to reinvent wheels, especially when the wheels are so good. Ninja is a one-trick pony that does
  its job extremely well. But it's just too low-level for most users, hence the need for a frontend.
* _Why not Python 3?_ Many, many deployed systems are still locked in Python 2 for various reasons.
  We want to be able to build on them.
* _Why Ninja? It's already yesterday's news! There are even faster builders._ Eh, if you ignore the
  initial configuration phase, and are properly multithreading your build (`-j` flag in Make), then
  the time you wait for the build to finish ends up depending on your compiler, not the build
  system. Ninja was chosen because of its marvelous minimalism, not its speed. Ninja is actually 
  [not much](http://david.rothlis.net/ninja-benchmark/) 
  [faster](http://hamelot.io/programming/make-vs-ninja-performance-comparison/)
  than Make. For a similarly minimalist build system, see [tup](http://gittup.org/tup/).

Similar Projects
----------------

* [bfg9000](https://github.com/jimporter/bfg9000): "bfg9000 is a cross-platform build configuration
  system with an emphasis on making it easy to define how to build your software."
* [emk](https://github.com/kmackay/emk): "A Python-based build tool."
* [Craftr](https://craftr.net/): "Craftr is a next generation build system based on Ninja and Python
  that features modular and cross-platform build definitions at the flexibility of a Python script
  and provides access to multiple levels of build automation abstraction."
* [Meson](http://mesonbuild.com/): "Meson is an open source build system meant to be both extremely
  fast, and, even more importantly, as user friendly as possible."
* [pyrate](https://github.com/pyrate-build/pyrate-build): "pyrate is a small python based build file
  generator targeting ninja(s)."
* [Waf](https://waf.io/): "The meta build system."
