"""
A simple connection proxy daemon.

In many ways, this is just a simplified version of the multiplexer daemon. It
shares the same backend mechanisms as the mux, but only manages a single
connection. Thus it uses the wire protocol outlined in `RFC 5734`_ exclusively.

.. _RFC 5734: http://tools.ietf.org/html/rfc5734
"""

import asyncore
import collections
import logging
import socket
import struct
import sys

import docopt
import ipaddr

from neuemux import utils
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


class Channel(asyncore.dispatcher):
    """
    """

    READING_LENGTH = 0
    READING_PAYLOAD = 1

    def __init__(self, sock):
        asyncore.dispatcher.__init__(self, sock)

        self.read_buffer = []
        self.write_buffer = collections.deque()

        # `state` refers to the current state we're at in the state machine,
        # and `remaining` refers to the number of bytes remaining to read
        # while in this state. We start off reading the length of a data unit,
        # and the the length is represented as a 32-bit network order integer,
        # thus it's four bytes long.
        self.state = self.READING_LENGTH
        self.remaining = 4

    def handle_read(self):
        chunk = self.recv(self.remaining)
        if chunk:
            self.remaining -= len(chunk)
            self.read_buffer.append(chunk)
            if self.remaining == 0:
                chunk = ''.join(self.read_buffer)
                self.read_buffer = []
                if self.state == self.READING_LENGTH:
                    self.state = self.READING_PAYLOAD
                    self.remaining, = struct.unpack('!I', chunk)
                    self.remaining -= 4
                elif self.state == self.READING_PAYLOAD:
                    self.state = self.READING_LENGTH
                    self.remaining = 4
                    self.on_read_frame(chunk)

    def writable(self):
        return len(self.write_buffer) > 0

    def handle_write(self):
        while len(self.write_buffer) > 0:
            head = self.write_buffer.popleft()
            sent = self.send(head)
            if sent != len(head):
                self.write_buffer.appendleft(head[sent:])
                break

    def on_read_frame(self, frame):
        """
        Triggered when a complete frame has been read.
        """
        pass

    def write_frame(self, frame):
        """
        Write a frame to this channel.
        """
        self.write_buffer.append(struct.pack('!I', len(frame) + 4) + frame)


class Acceptor(asyncore.dispatcher):
    """
    Accepts incoming requests, spawning dispatchers to deal with them.
    """

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

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

    config = utils.load_configuration(DEFAULTS, opts['--config'])

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

    # config_dir = os.path.dirname(os.path.realpath(opts['--config']))

    Acceptor(addr, port)
    asyncore.loop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
