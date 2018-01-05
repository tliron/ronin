#!/bin/bash

PYTHON=python3

DIR=$1

if [ -z "$DIR" ]; then
	DIR=$(dirname "$(readlink -f "$0")")
fi

if [ -d "$DIR/ronin" ]; then
	echo "Cannot create 'ronin' executable in '$DIR' because there already is a 'ronin' directory"
	exit 1
fi

pip --quiet install pex

pex \
	ronin \
	--output-file="$DIR/ronin" \
	--python=$PYTHON \
	--python-shebang="#!/usr/bin/env $PYTHON"

echo "Created '$DIR/ronin'"

NINJA=$(which 'ninja')
if [ -n "$NINJA" ]; then
	if [ -d "$DIR/ninja" ]; then
		echo "Cannot create 'ninja' executable in '$DIR' because there already is a 'ninja' directory"
		exit 1
	fi
	cp "$NINJA" "$DIR/ninja"
	echo "Created '$DIR/ninja'" 
else
	echo "ninja not found, so ronin will look for a pre-installed ninja"
fi
