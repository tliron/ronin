#!/bin/bash

HERE=$(dirname "$(readlink -f "$0")")

"$HERE/cross/build.py"
"$HERE/gcc/build1.py"
"$HERE/gcc/build2.py"
"$HERE/gcc/build3.py"
"$HERE/go/build.py"
"$HERE/java/build.py"
"$HERE/multi/build.py"
"$HERE/rust/build1.py"
"$HERE/rust/build2.py"
"$HERE/sdl/build.py"
"$HERE/vala/build1.py"
"$HERE/vala/build2.py"
