#!/usr/bin/env python

from __future__ import with_statement

import os.path

from setuptools import setup, find_packages


def read(filename):
    """
    Read files relative to this file.
    """
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with open(full_path, 'r') as fh:
        return fh.read()


def read_requirements(requirements_path):
    """
    Read a requirements file, stripping out the detritus.
    """
    requirements = []
    with open(requirements_path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if line != '' and not line.startswith(('#', 'git+')):
                requirements.append(line)
    return requirements


setup(
    name='neuemux',
    version='0.1.0',
    description='EPP reverse proxy daemons',
    long_description=read('README') + "\n" + read('ChangeLog'),
    url='https://github.com/kgaughan/neuemux/',
    license='MIT',
    packages=find_packages(exclude='tests'),
    zip_safe=False,
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    test_suite='tests',

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
