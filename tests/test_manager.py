import pytest

from sim800.manager import SIM800
from sim800.commands.command import Command
from sim800.results.result import Result
import io


class BytesIO(io.BytesIO):
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


@pytest.fixture
def sim800():
    s = SIM800()
    s.serial = BytesIO()
    return s


def test_sim800_send_command(sim800):
    cmd = Command('+COPS?', ['+COPS: '])
    sim800.send_command(cmd, recv_result=False)

    assert sim800.serial.getvalue() == b'AT+COPS?\r'

    sim800.serial.write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n')
    sim800.serial.seek(0)

    r = sim800.recv_command_result(cmd)
    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

