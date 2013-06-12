"""

"""

import asyncore
import collections
import socket
import struct


_HEADER = struct.Struct('!L')


class Listener(asyncore.dispatcher):
    """
    Listens for incoming requests, spawning dispatchers to deal with them.
    """

    def __init__(self, host, port, backlog=5):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(backlog)


class Channel(asyncore.dispatcher):
    """
    RFC5734_ channel.

    .. _RFC5734: http://tools.ietf.org/html/rfc5734
    """

    # States.
    READING_LENGTH = object()
    READING_PAYLOAD = object()

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
        self.remaining = _HEADER.size

    def handle_read(self):
        chunk = self.recv(self.remaining)
        if chunk:
            self.remaining -= len(chunk)
            self.read_buffer.append(chunk)
            if self.remaining == 0:
                chunk = ''.join(self.read_buffer)
                self.read_buffer = []
                if self.state is self.READING_LENGTH:
                    self.state = self.READING_PAYLOAD
                    self.remaining, = _HEADER.unpack(chunk)
                    self.remaining -= _HEADER.size
                elif self.state is self.READING_PAYLOAD:
                    self.state = self.READING_LENGTH
                    self.remaining = _HEADER.size
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
        size = len(frame) + _HEADER.size
        self.write_buffer.append(_HEADER.pack(size) + frame)
