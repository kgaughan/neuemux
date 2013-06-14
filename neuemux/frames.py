"""
Support for basic EPP frame construction and parsing.
"""

from neuemux import xmlutils


ROOT = 'urn:ietf:params:xml:ns:epp-1.0'

HELLO = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<epp xmlns="urn:ietf:params:xml:ns:epp-1.0"><hello/></epp>'
)

LOGOUT = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">'
    '<command><logout/><clTRID>neuemux-logout</clTRID></command>'
    '</epp>'
)


def login(uname, pwd, objs=(), exts=(), lang='en'):
    """
    Construct a login frame.
    """
    xml = xmlutils.XMLBuilder()
    with xml.within('epp', xmlns=ROOT):
        with xml.within('command'):
            with xml.within('login'):
                xml.tag('clID', uname)
                xml.tag('pw', pwd)
                with xml.within('options'):
                    xml.tag('version', '1.0')
                    xml.tag('lang', lang)
                with xml.within('svcs'):
                    for obj in objs:
                        xml.tag('objURI', obj)
                    with xml.within('svcExtension'):
                        for ext in exts:
                            xml.tag('extURI', ext)
            xml.tag('clTRID', 'neuemux-login')
    return xml.as_string()
