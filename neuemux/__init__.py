"""
An EPP_ connection multiplexing daemon and client.

.. _EPP: http://tools.ietf.org/html/rfc5730

Please note that this is not intended to actually *implement* the protocol,
just to multiplex connections from multiple clients to multiple servers, and
maintain those connections properly over extended periods.
"""


__version__ = '0.0.1'
__author__ = 'Keith Gaughan'
__email__ = 'k@stereochro.me'
