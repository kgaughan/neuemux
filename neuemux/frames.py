"""
Support for basic EPP frame construction and parsing.
"""

import uuid

from neuemux import xmlutils


ROOT = 'urn:ietf:params:xml:ns:epp-1.0'

HELLO = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<epp xmlns="urn:ietf:params:xml:ns:epp-1.0"><hello/></epp>'
)


def login(uname, pwd, objs=(), exts=(), lang='en', trid=None):
    """
    Construct a login frame.
    """
    if trid is None:
        trid = uuid.uuid1()

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
            xml.tag('clTRID', trid)
    return xml.as_string()


def logout(trid=None):
    """
    Construct a logout frame.
    """
    if trid is None:
        trid = uuid.uuid1()

    xml = xmlutils.XMLBuilder()
    with xml.within('epp', xmlns=ROOT):
        with xml.within('command'):
            xml.tag('logout')
            xml.tag('clTRID', trid)
    return xml.as_string()
