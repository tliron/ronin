#!/usr/bin/env python

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

    packages=['ronin'])
