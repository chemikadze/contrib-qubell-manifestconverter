#!/usr/bin/env python

import os
from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

setup(name='contrib-qubell-manifestconverter',
      version='0.1',
      description='Tonomi/Qubell manifest conversions',
      long_description=open('README.md').read(),
      author='Nikolay Sokolov',
      author_email='nsokolov@qubell.com',
      url='https://github.com/chemikadze/contrib-qubell-manifestconverter',
      packages=find_packages(),
      package_data={'': ['README.md']},
      include_package_data=True,
      install_requires=open("requirements.txt").read().split(),
      tests_require=open("requirements-test.txt").read().split(),
      test_suite="nosetests",
      entry_points='''
        [console_scripts]
        nomi-convert=nomiconvert.__main__:nomi_convert
    '''
      )
