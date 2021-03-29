import pytest

import io
from sim800.manager import SIM800, BufferedReader, TimeoutException


class BytesIO(io.BytesIO):
    def __init__(self):
        self.after_write = None
        self.seek_begin = False

    def read_until(self, expected, size=None):
        ignore_size = size is None

        res = b''
        res += self.read(1)
        if size is not None:
            size -= 1
        while not res.endswith(expected) and (ignore_size or size > 0):
            res += self.read(1)
            if size is not None:
                size -= 1
        return res

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
    s.buffered_reader = BufferedReader(s.serial, timeout=timeout)
    return s

