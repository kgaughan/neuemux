"""
The actual daemon itself.
"""

from ConfigParser import SafeConfigParser
import logging
import logging.config
import os.path
import sys

import diesel


USAGE = "Usage: %s <config>"

# Default EPP wire protocol port.
EPP_PORT = 700
# Unofficial port used by the EPPMUX wire protocol.
MUX_PORT = 1700

logger = logging.getLogger('neuemux.muxd')


def respond(addr):
    """
    A very basic responder to make sure everything works.
    """
    diesel.send('Hello, %s:%d!\n' % addr)


def make_default_config_parser():
    """
    Creates a config parser with the bare minimum of defaults.
    """
    defaults = {
        'iface': '127.0.0.1',
        'port': str(MUX_PORT),
    }

    parser = SafeConfigParser()
    for section in ('muxd',):
        parser.add_section(section)
    for key, value in defaults.iteritems():
        parser.set('muxd', key, value)

    return parser


def main():
    """
    Execute the daemon.
    """
    if len(sys.argv) != 2:
        print >> sys.stderr, USAGE % os.path.basename(sys.argv[0])
        return 1

    logging.config.fileConfig(sys.argv[1])

    parser = make_default_config_parser()

    try:
        logger.info("Reading config file at '%s'", sys.argv[1])
        parser.read(sys.argv[1])

        iface = parser.get('muxd', 'iface')
        port = parser.getint('muxd', 'port')
        logger.info('Listen on %s:%d', iface, port)
    except Exception, ex:  # pylint: disable-msg=W0703
        print >> sys.stderr, 'Could not parse config file: %s' % str(ex)
        return 1

    logger.info('Creating service')
    service = diesel.Service(respond, port, iface)
    logger.info('Starting...')
    diesel.quickstart(service)
    return 0


if __name__ == '__main__':
    sys.exit(main())
