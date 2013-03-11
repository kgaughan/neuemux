"""
A simple connection proxy daemon.

In many ways, this is just a simplified version of the multiplexer daemon. It
shares the same backend mechanisms as the mux, but only manages a single
connection. Thus it uses the wire protocol outlined in `RFC 5734`_ exclusively.

.. _RFC 5734: http://tools.ietf.org/html/rfc5734
"""

import ConfigParser
import sys

import docopt
import twiggy
import twiggy.levels

from neuemux.version import __version__


USAGE = """
An EPP reverse proxy.

Usage:
  epp-proxyd SERVER [--config=PATH] [--iface=IFACE] [--port=PORT]
  epp-proxyd -h | --help
  epp-proxyd --version

Options:
  -h, --help     Show this screen.
  --version      Show version.
  --config=PATH  Configuration file to use.
                 [default: /etc/neuemux/proxyd.ini]
  --iface=IFACE  Interface to bind to.
                 [default: 127.0.0.1]
  --port=PORT    Port to listen on when bound.
                 [default: 700]
"""

DEFAULTS = {
    'common': {
        'namespaces': '\n'.join([
            'urn:ietf:params:xml:ns:epp-1.0',
            'urn:ietf:params:xml:ns:domain-1.0',
            'urn:ietf:params:xml:ns:host-1.0',
            'urn:ietf:params:xml:ns:contact-1.0',
            'urn:ietf:params:xml:ns:secDNS-1.0',
            'urn:ietf:params:xml:ns:secDNS-1.1',
            'urn:ietf:params:xml:ns:e164epp-1.0',
            'urn:ietf:params:xml:ns:rgp-1.0',
        ]),
        'log_level': 'INFO',
    },
}

logger = twiggy.log.name('neuemux.proxyd')


class Config(ConfigParser.RawConfigParser):
    """
    A version of `ConfigParser.RawConfigParser` that sets up default values
    and sections.
    """

    def __init__(self, defaults):
        ConfigParser.RawConfigParser.__init__(self)
        for section, kvs in defaults.iteritems():
            self.add_section(section)
            for key, value in kvs.iteritems():
                self.set(section, key, value)


def main():
    """
    Execute the daemon.
    """
    opts = docopt.docopt(USAGE, sys.argv[1:], version=__version__)

    # Load the configuration and set up logging.
    config = Config(DEFAULTS)
    has_config = len(config.read(opts['--config'])) > 0
    logger.min_level = twiggy.levels.name2level(
        config.get('common', 'log_level'))
    if not has_config:
        logger.warning('Config file {0} not found', opts['--config'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
