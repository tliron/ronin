#!/bin/bash

VERSION=1.1.2

HERE=$(dirname "$(readlink -f "$0")")
cd "$HERE"

sudo apt install pandoc
pip install twine pypandoc

./setup.py sdist bdist_wheel --universal

gpg --detach-sign -a dist/ronin-$VERSION.tar.gz
gpg --detach-sign -a dist/ronin-$VERSION-py2.py3-none-any.whl

twine upload \
	dist/ronin-$VERSION.tar.gz \
	dist/ronin-$VERSION.tar.gz.asc \
	dist/ronin-$VERSION-py2.py3-none-any.whl \
	dist/ronin-$VERSION-py2.py3-none-any.whl.asc
