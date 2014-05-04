#!/usr/bin/env python

from __future__ import with_statement

import buildkit
from setuptools import setup, find_packages


setup(
    name='neuemux',
    version='0.1.0',
    description='EPP reverse proxy daemons',
    long_description=buildkit.read('README'),
    url='https://github.com/kgaughan/neuemux/',
    license='MIT',
    packages=find_packages(exclude='tests'),
    zip_safe=False,
    install_requires=buildkit.read_requirements('requirements.txt'),
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

    author='Keith Gaughan',
    author_email='k@stereochro.me',
)
