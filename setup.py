#!/usr/bin/env python
from setuptools import setup
import glob
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), 'r') as f:
  long_description = f.read()

with open(path.join(here, 'requirements.txt'), 'r') as f:
  required_packages = f.read()

setup(name='gar',
      version='0.1.0',

      author="Stanislaw Bogatkin",
      author_email="sbog@sbog.ru",

      description="Gar is Gerrit Add Reviewers tool to easy add reviewers to your patchset.",
      long_description=long_description,
      url='https://github.com/sorrowless/gar',
      keywords="gerrit openstack review automation",
      license="GPL",

      packages=['gar'],
      install_requires=required_packages,

      package_data= {
        '': ['requirements.txt','README.md'],
      },

      entry_points={
        'console_scripts': [
          'gar=gar.gar:main',
        ],
      },
)
