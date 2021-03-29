from sim800.manager import SIM800
from sim800.commands.command import Command


def test_at_command(sim800):
    s = sim800
    at_cmd = Command("")
    s.serial.after_next_write(b'AT\r\r\nOK\r\n')
    f, r = s.send_command(at_cmd)
    assert f.success
    assert f.str_result == "OK"


def test_revision(sim800):
    s = sim800
    rev_cmd = Command("+GSV", ['SIM', 'Rev'])
    s.serial.after_next_write(b'AT+GSV\r\r\nSIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:***REMOVED***\r\n\r\nOK\r\n')
    f, r = s.send_command(rev_cmd)
    assert f.success
    assert r.str_result == "SIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:***REMOVED***"

def test_imei(sim800):
    s = sim800
    rev_cmd = Command("+GSN", ['8626'])
    s.serial.after_next_write(b'AT+GSV\r\r\n***REMOVED***\r\n\r\nOK\r\n')
    f, r = s.send_command(rev_cmd)
    assert f.success
    assert r.str_result == "***REMOVED***"

