#!/usr/bin/env python

import os
from setuptools import Command, setup
import subprocess
import uuid

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements


NAME = 'gamebattles'
DESCRIPTION = 'cli for getting and reporting matches on ' \
              'http://gamebattles.majorleaguegaming.com/'
URL = 'https://github.com/BradleyGrantham/gamebattles-match-finder'
EMAIL = 'bradley.grantham@bath.edu'
AUTHOR = 'Bradley Grantham'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.0.1'  # update with every release
INSTALL_REQS = parse_requirements('requirements.txt',
                                  session=uuid.uuid1())
REQUIRED = [str(req.req) for req in INSTALL_REQS]


class Clean(Command):
    """Clean python setup build files."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """List of temporary objects"""

        path = os.path.dirname(os.path.abspath(__file__))

        subprocess.call(['rm', '-rf', os.path.join(path, 'dist')])
        subprocess.call(['rm', '-rf', os.path.join(path, 'metastore_db')])
        subprocess.call(['rm', '-rf', os.path.join(path, '.cache')])
        subprocess.call(['rm', '-rf', os.path.join(path, '.eggs')])
        subprocess.call(['rm', '-rf', os.path.join(path, 'spanner.egg-info')])
        subprocess.call(['rm', '-rf', os.path.join(path, 'spanner.egg-info')])
        subprocess.call(['rm', '-rf', os.path.join(path, '__pycache__')])
        subprocess.call(['rm', '-rf', os.path.join(path, 'tests', '__pycache__')])
        subprocess.call(['rm', '-rf', os.path.join(path, 'tests', '.cache')])
        subprocess.call(['find', path, '-name', '*.pyc', '-type', 'f', '-delete'])
        subprocess.call(['find', path, '-name', '*.log', '-type', 'f', '-delete'])


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      python_requires=REQUIRES_PYTHON,
      packages=['gamebattles'],
      entry_points={
          'console_scripts': [
              'gb=gamebattles:__main__.cli',
          ]
      },
      cmdclass={'clean': Clean},
      install_requires=REQUIRED,
      )
