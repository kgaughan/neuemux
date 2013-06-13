"""
A simple connection proxy daemon.

In many ways, this is just a simplified version of the multiplexer daemon. It
shares the same backend mechanisms as the mux, but only manages a single
connection. Thus it uses the wire protocol outlined in `RFC 5734`_ exclusively.

.. _RFC 5734: http://tools.ietf.org/html/rfc5734
"""

import asyncore
import logging
import os.path
import sys

import docopt
import ipaddr

from neuemux import protocols, utils
from neuemux.version import __version__


USAGE = """
An EPP reverse proxy.

Usage:
  epp-proxyd SERVER [--config=PATH] [--bind=ADDR] [--port=PORT]
  epp-proxyd -h | --help
  epp-proxyd --version

Options:
  -h, --help     Show this screen.
  --version      Show version.
  --config=PATH  Configuration file to use.
                 [default: /etc/neuemux/proxyd.ini]
  --bind=ADDR    Interface address to bind to.
                 [default: 127.0.0.1]
  --port=PORT    Port to listen on when bound.
                 [default: 700]
"""

DEFAULTS = """
[common]
namespaces=
    urn:ietf:params:xml:ns:epp-1.0
    urn:ietf:params:xml:ns:domain-1.0
    urn:ietf:params:xml:ns:host-1.0
    urn:ietf:params:xml:ns:contact-1.0
    urn:ietf:params:xml:ns:secDNS-1.0
    urn:ietf:params:xml:ns:secDNS-1.1
    urn:ietf:params:xml:ns:e164epp-1.0
    urn:ietf:params:xml:ns:rgp-1.0
"""

logger = logging.getLogger('neuemux.proxyd')


class Listener(protocols.Listener):
    """
    Listener for proxyd.
    """

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logger.info('Incoming connection from %s', repr(addr))


def main():
    """
    Execute the daemon.
    """
    opts = docopt.docopt(USAGE, sys.argv[1:], version=__version__)

    if not os.path.isfile(opts['--config']):
        print >> sys.stderr, "Configuration not found: %s" % opts['--config']
        return 1

    config = utils.load_configuration(DEFAULTS, opts['--config'])

    # Check the options for well-formedness.
    try:
        # Will raise a ValueError if it's malformed.
        ipaddr.IPAddress(opts['--bind'])
        addr = opts['--bind']

        try:
            port = int(opts['--port'])
        except ValueError:
            raise ValueError('Bad port number: "%s"' % opts['--port'])
        if not 0 <= int(opts['--port']) < 65536:
            raise ValueError('Bad port number: "%d"' % port)

        if not config.has_section('server:' + opts['SERVER']):
            raise ValueError("No such server: '%s'" % opts['SERVER'])
    except ValueError, exc:
        print >> sys.stderr, str(exc)
        return 1

    # config_dir = os.path.dirname(os.path.realpath(opts['--config']))

    Listener(addr, port)
    asyncore.loop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
