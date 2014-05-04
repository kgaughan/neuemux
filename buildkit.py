from __future__ import with_statement

import os.path


def read(filename):
    """Read files relative to this file."""
    full_path = os.path.join(os.path.dirname(__file__), filename)
    with open(full_path, 'r') as fh:
        return fh.read()


def read_requirements(requirements_path):
    """Read a requirements file, stripping out the detritus."""
    requirements = []
    with open(requirements_path, 'r') as fh:
        for line in fh:
            line = line.strip()
            if line != '' and not line.startswith(('#', 'svn+', 'git+')):
                requirements.append(line)
    return requirements
