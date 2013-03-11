#!/usr/bin/env python

from __future__ import with_statement

from setuptools import setup, find_packages
from buildkit import *


META = get_metadata('neuemux/version.py')


setup(
    name='neuemux',
    version=META['version'],
    description='EPP reverse proxy daemons',
    long_description=read('README'),
    url='https://github.com/kgaughan/neuemux/',
    license='MIT',
    packages=find_packages(exclude='tests'),
    zip_safe=False,
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'epp-proxyd = neuemux.proxyd:main',
            'epp-muxd = neuemux.muxd:main',
        ],
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: System :: Networking',
    ],

    author=META['author'],
    author_email=META['email']
)
