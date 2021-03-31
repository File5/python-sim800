import pytest

import serial
from sim800.manager import SIM800, TimeoutException
from sim800.commands.command import Command
from sim800.results.result import Result
import sim800.results.unsolicited as unsolicited


def test_bytes_io_read_until_expected(bytes_io):
    s = bytes_io()
    s.write(b'0123456789')
    s.seek(0)

    assert s.read_until(b'5') == b'012345'

def test_bytes_io_read_until_size(bytes_io):
    s = bytes_io()
    s.write(b'0123456789')
    s.seek(0)

    assert s.read_until(b'5', 4) == b'0123'

def test_bytes_io_after_next_write(bytes_io):
    s = bytes_io()
    s.after_next_write(b'\r\nOK\r\n')
    
    s.write(b'AT\r')

    assert s.getvalue() == b'AT\r\r\nOK\r\n'


def test_sim800_readline(sim800):
    data = b'AT+GSV;+GSN\r\r\nSIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:9999999SIM800L99\r\n\r\n862643039999994\r\n\r\nOK\r\n'

    s = sim800
    s.serial.write(data)
    s.serial.seek(0)

    assert s.readline() == b'AT+GSV;+GSN\r'
    assert s.readline() == b'\r\n'
    assert s.readline() == b'SIMCOM_Ltd\r\n'
    assert s.readline() == b'SIMCOM_SIM800L\r\n'
    assert s.readline() == b'Revision:9999999SIM800L99\r\n'
    assert s.readline() == b'\r\n'
    assert s.readline() == b'862643039999994\r\n'
    assert s.readline() == b'\r\n'
    assert s.readline() == b'OK\r\n'

def test_sim800_read_echo_or_result(sim800):
    data = b'AT+GSV;+GSN\r\r\nSIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:9999999SIM800L99\r\n\r\n862643039999994\r\n\r\nOK\r\n'

    s = sim800
    s.serial.write(data)
    s.serial.seek(0)

    assert s.read_echo_or_result() == b'AT+GSV;+GSN\r'
    assert s.read_echo_or_result() == b'\r\nSIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:9999999SIM800L99\r\n'
    assert s.read_echo_or_result() == b'\r\n862643039999994\r\n'
    assert s.read_echo_or_result() == b'\r\nOK\r\n'

def test_sim800_send_command_recv_recv_result(sim800):
    sim800.serial.after_next_write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n')
    cmd = Command('+COPS?', ['+COPS: '])
    f, r = sim800.send_command(cmd)

    assert sim800.serial.getvalue() == b'AT+COPS?\r' + b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n'

    assert f.success
    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

def test_sim800_send_command_recv_recv_result_unsolicited_before_command(sim800):
    sim800.serial.write(b'\r\n+CMTI: "ME",1\r\n')
    sim800.serial.after_next_write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n')
    cmd = Command('+COPS?', ['+COPS: '])
    f, r = sim800.send_command(cmd)

    assert sim800.serial.getvalue() == b'\r\n+CMTI: "ME",1\r\nAT+COPS?\r' + b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n'

    assert f.success
    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

    assert len(sim800.unsolicited) == 1
    u = sim800.unsolicited[0]
    assert type(u) is unsolicited.NewMessageResult
    assert u.memory == 'ME'
    assert u.index == 1

def test_sim800_send_command_recv_recv_result_unsolicited_after_command(sim800):
    sim800.serial.after_next_write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n' + b'\r\n+CMTI: "ME",1\r\n')
    cmd = Command('+COPS?', ['+COPS: '])
    f, r = sim800.send_command(cmd)

    assert sim800.serial.getvalue() == b'AT+COPS?\r' + b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n' + b'\r\n+CMTI: "ME",1\r\n'

    assert f.success
    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

    assert len(sim800.unsolicited) == 0

    u = sim800.recv_unsolicited()
    assert len(sim800.unsolicited) == 0
    assert type(u) is unsolicited.NewMessageResult
    assert u.memory == 'ME'
    assert u.index == 1

def test_sim800_send_command_recv_command_result(sim800):
    cmd = Command('+COPS?', ['+COPS: '])
    sim800.send_command(cmd, recv_result=False)

    assert sim800.serial.getvalue() == b'AT+COPS?\r'

    sim800.serial.write(b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n\r\nOK\r\n')
    sim800.serial.seek(0)

    f, r = sim800.recv_command_result(cmd)
    assert f.success
    assert type(r) is Result
    assert r.str_result == '+COPS: 0,0,"CHINA MOBILE"'
    assert r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

def test_sim800_recv_unsolicited_timeout():
    sim800 = SIM800(timeout=3)
    timeout = sim800.serial.timeout
    sim800.serial = serial.serial_for_url('loop://', timeout=timeout)
    with pytest.raises(TimeoutException):
        u = sim800.recv_unsolicited()

