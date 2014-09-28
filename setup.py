#!/usr/bin/env python

from distutils.core import setup

setup(name='parsec-hydra-backend',
      version='1.0',
      description='Parsec Hydra backend',
      url='http://www.python.org/sigs/distutils-sig/',
      packages=['distutils', 'distutils.command'],
      requires=['flask', 'flask-socketio', 'pyuserinput', 'pybluez']
     )
