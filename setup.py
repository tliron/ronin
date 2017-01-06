#!/usr/bin/env python

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
import sys

if sys.version_info < (2, 7):
    sys.exit('Ronin requires Python 2.7+')
if sys.version_info >= (3, 0):
    sys.exit('Ronin does not support Python 3')

setup(
    name='ronin',
    version='0.1',
    description='Ronin',
    license='Apache License Version 2.0',

    author='Tal Liron',
    author_email='tal.liron@gmail.com',
    
    url='https://github.com/tliron/ronin',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools'],

    packages=['ronin'],
    
    install_requires=[
        'blessings==1.6',
        'colorama==0.2.4',
        'glob2==0.5'])
