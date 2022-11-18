"""
Utilities.
"""

import ConfigParser
import contextlib
import glob
import logging
import logging.config
import re
try:
    import cStringIO as stringio
except ImportError:
    import StringIO as stringio

import pkg_resources


def get_version():
    pkg_resources.get_distribution('neuemux').version


def load_configuration(defaults=None, config_path=None):
    """
    Load configuration.
    """
    config = ConfigParser.RawConfigParser()

    # Defaults, if any.
    if defaults is not None:
        with contextlib.closing(stringio.StringIO(defaults)) as fp:
            config.readfp(fp)

    # Main configuration file, if any.
    if config_path is None:
        # Ensure logging is at least configured to a minimum level.
        logging.basicConfig()
    else:
        config.read(config_path)
        logging.config.fileConfig(config_path)

    # Load in any additional config files.
    if config.has_option('include', 'files'):
        config.read(glob.glob(config.get('include', 'files')))

    return config


class LoopDetected(Exception):
    """
    Loop detected in configuration.
    """


def get_nested_config(config, prefix, name):
    """
    Extract the given named config.
    """
    walked = set()
    result = {}
    while name is not None:
        section = f'{prefix}:{name}'
        walked.add(name)
        next_name = None
        for key, value in config.items(section):
            if key == '_base':
                next_name = value
                if next_name in walked:
                    raise LoopDetected("Config loop found for '%s'" % section)
            elif key not in result:
                result[key] = value
        name = next_name
    return result


OBJECT_REF_PATTERN = re.compile(r"""
    ^
    (?P<module>
        [a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*
    )
    :
    (?P<object>
        [a-z_][a-z0-9_]*
    )
    $
    """, re.I | re.X)


def load_object(object_ref):
    """
    Attempts to import the named object. The object reference is a name in
    the form 'module.name:object_name'.
    """
    matches = OBJECT_REF_PATTERN.match(object_ref)
    if not matches:
        raise ValueError("Malformed object reference: '%s'" % object_ref)

    module_name = matches.group('module')
    object_name = matches.group('object')

    module = __import__(module_name, fromlist=[object_name])
    return getattr(module, object_name)
