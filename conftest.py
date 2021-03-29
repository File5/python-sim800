import pytest

import io
import serial
from sim800.manager import SIM800, TimeoutException


class BytesIO(io.BytesIO):
    def __init__(self, *args, **kwargs):
        self._timeout = 1
        if 'timeout' in kwargs:
            self._timeout = kwargs.pop('timeout')
        super().__init__(*args, **kwargs)
        self.after_write = None
        self.seek_begin = False

    def read_until(self, expected=b'\n', size=None):
        lenterm = len(expected)
        line = bytearray()
        timeout = serial.serialutil.Timeout(self._timeout)
        while True:
            c = self.read(1)
            if c:
                line += c
                if line[-lenterm:] == expected:
                    break
                if size is not None and len(line) >= size:
                    break
            else:
                break
            if timeout.expired():
                break
        return bytes(line)

    def after_next_write(self, b, seek_begin=True):
        self.after_write = b
        self.seek_begin = seek_begin

    def write(self, *args, **kwargs):
        super().write(*args, **kwargs)
        if self.after_write is not None:
            super().write(self.after_write)
            self.after_write = None
        if self.seek_begin:
            self.seek(0)
            self.seek_begin = False


@pytest.fixture
def bytes_io():
    return BytesIO


@pytest.fixture
def sim800():
    s = SIM800()
    timeout = s.serial.timeout
    s.serial = BytesIO()
    return s

