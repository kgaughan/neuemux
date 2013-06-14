"""
XML utilities.

Copyright (c) Keith Gaughan, 2013.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import contextlib
from xml.sax import saxutils
try:
    import cStringIO as stringio
except ImportError:
    import StringIO as stringio


class XMLBuilder(object):
    """
    XML document builder. The code is purposely namespace ignorant: it's up to
    user to supply appropriate `xmlns` attributes as needed.

    >>> xml = XMLBuilder()
    >>> with xml.within('root', xmlns='tag:talideon.com,2013:test'):
    ...     xml += 'Before'
    ...     with xml.within('leaf'):
    ...         xml += 'Within'
    ...     xml += 'After'
    ...     xml.tag('leaf', 'Another')
    >>> print xml.as_string()
    <?xml version="1.0" encoding="utf-8"?>
    <root xmlns="tag:talideon.com,2013:test">Before<leaf>Within</leaf>After<leaf>Another</leaf></root>
    """

    def __init__(self, out=None, encoding='utf-8'):
        """
        `out` should be a file-like object to write the document to. If none
        is provided, a buffer is created.

        Note that if you provide your own, `as_string()` will return `None`
        as no other sensible value can be returned.
        """
        if out is None:
            self.buffer = stringio.StringIO()
            out = self.buffer
        else:
            self.buffer = None
        self.generator = saxutils.XMLGenerator(out, encoding)
        self.generator.startDocument()

    @contextlib.contextmanager
    def within(self, tag, **attrs):
        """
        Generates an element containing nested elements.
        """
        self.generator.startElement(tag, attrs)
        yield
        self.generator.endElement(tag)

    def tag(self, tag, *values, **attrs):
        """
        Generates a simple element.
        """
        self.generator.startElement(tag, attrs)
        for value in values:
            self.generator.characters(value)
        self.generator.endElement(tag)

    def append(self, other):
        """
        Append the string to this document.
        """
        self.generator.characters(other)
        return self

    def as_string(self):
        """
        If using the built-in buffer, get its current contents.
        """
        if self.buffer is None:
            return None
        return self.buffer.getvalue()

    def close(self):
        """
        If using the built-in buffer, clean it up.
        """
        if self.buffer is not None:
            self.buffer.close()
            self.buffer = None

    # Shortcuts.
    __iadd__ = append
    __str__ = as_string
