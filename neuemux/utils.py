"""
Utilities.
"""

import re


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
