"""
A simple connection proxy daemon.

In many ways, this is just a simplified version of the multiplexer daemon. It
shares the same backend mechanisms as the mux, but only manages a single
connection. Thus it uses the wire protocol outlined in `RFC 5734`_ exclusively.

.. _RFC 5734: http://tools.ietf.org/html/rfc5734
"""

import ConfigParser
import sys

import diesel
import docopt
import ipaddr
import twiggy
import twiggy.levels

from neuemux.version import __version__


USAGE = """
An EPP reverse proxy.

Usage:
  epp-proxyd SERVER [--config=PATH] [--addr=ADDR] [--port=PORT]
  epp-proxyd -h | --help
  epp-proxyd --version

Options:
  -h, --help     Show this screen.
  --version      Show version.
  --config=PATH  Configuration file to use.
                 [default: /etc/neuemux/proxyd.ini]
  --addr=ADDR    Interface address to bind to.
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


def respond(addr):
    """
    A very basic responder to make sure everything works.
    """
    diesel.send('Hello, %s:%d!\n' % addr)


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

    # Check the options for well-formedness.
    try:
        # Will raise a ValueError if it's malformed.
        ipaddr.IPAddress(opts['--addr'])
        addr = opts['--addr']

        try:
            port = int(opts['--port'])
        except ValueError:
            raise ValueError('Bad port number: "%s"' % opts['--port'])
        if not 0 <= int(opts['--port']) < 65536:
            raise ValueError('Bad port number: "%d"' % port)

        for prefix in ('server:', 'derive:'):
            if config.has_section(prefix + opts['SERVER']):
                break
        else:
            raise ValueError("No such server: '%s'" % opts['SERVER'])
    except ValueError, exc:
        print >> sys.stderr, str(exc)
        return 1

    logger.info('Listening on {0}:{1}', addr, port)
    service = diesel.Service(respond, port, addr)

    diesel.quickstart(service)
    return 0


if __name__ == '__main__':
    sys.exit(main())
