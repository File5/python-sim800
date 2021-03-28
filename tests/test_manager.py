import pytest

from sim800.manager import SIM800
from sim800.commands.command import Command
from sim800.results.result import Result
import io


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

def test_bytes_io_read_until_expected():
    s = BytesIO()
    s.write(b'0123456789')
    s.seek(0)

    assert s.read_until(b'5') == b'012345'

def test_bytes_io_read_until_size():
    s = BytesIO()
    s.write(b'0123456789')
    s.seek(0)

    assert s.read_until(b'5', 4) == b'0123'

def test_bytes_io_after_next_write():
    s = BytesIO()
    s.after_next_write(b'\r\nOK\r\n')
    
    s.write(b'AT\r')

    assert s.getvalue() == b'AT\r\r\nOK\r\n'


@pytest.fixture
def sim800():
    s = SIM800()
    s.serial = BytesIO()
    return s


def test_sim800_send_command_recv_recv_result(sim800):
    sim800.serial.after_next_write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n')
    cmd = Command('+COPS?', ['+COPS: '])
    r = sim800.send_command(cmd)

    assert sim800.serial.getvalue() == b'AT+COPS?\r' + b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n'

    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

def test_sim800_send_command_recv_command_result(sim800):
    cmd = Command('+COPS?', ['+COPS: '])
    sim800.send_command(cmd, recv_result=False)

    assert sim800.serial.getvalue() == b'AT+COPS?\r'

    sim800.serial.write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n')
    sim800.serial.seek(0)

    r = sim800.recv_command_result(cmd)
    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

