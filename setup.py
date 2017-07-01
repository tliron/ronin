#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016-2017 Tal Liron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup
from sys import version_info
import os

if version_info < (2, 7):
    exit(u'Rōnin requires Python 2.7+')
if version_info >= (3, 0):
    exit(u'Rōnin does not support Python 3')

HERE = os.path.dirname(__file__)

try:
    # This is a nice little hack to get a ReST version of the README.md file to show up on PyPI.
    # Requires: 
    #   sudo apt install pandoc
    #   pip install pypandoc
    import pypandoc # @UnresolvedImport
    long_description = pypandoc.convert(os.path.join(HERE, 'README.md'), 'rst')
except(IOError, ImportError):
    long_description = open(os.path.join(HERE, 'README.md')).read()

execfile(os.path.join(HERE, 'ronin', 'version.py'))

setup(
    name='ronin',
    version=VERSION, # @UndefinedVariable
    description=u'Rōnin',
    long_description=long_description,
    license='Apache License Version 2.0',

    author='Tal Liron',
    author_email='tal.liron@gmail.com',
    
    url='https://github.com/tliron/ronin',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools'],

    packages=['ronin',
              'ronin.binutils',
              'ronin.files',
              'ronin.gcc',
              'ronin.go',
              'ronin.java',
              'ronin.pkg_config',
              'ronin.qt',
              'ronin.rust',
              'ronin.sdl',
              'ronin.utils',
              'ronin.vala'],
    
    install_requires=[
        'blessings>=1.6, <2.0',
        'colorama>=0.3.9, <2.0.0',
        'glob2>=0.5, <=2.0'])
