from sim800.manager import SIM800
from sim800.commands.command import Command


def test_at_command(sim800):
    s = SIM800('/dev/ttyAMA0', timeout=3)
    at_cmd = Command("")
    f, r = s.send_command(at_cmd)
    assert f.success
    assert f.str_result == "OK"


def test_revision(sim800):
    s = SIM800('/dev/ttyAMA0', timeout=3)
    rev_cmd = Command("+GSV", ['SIM', 'Rev'])
    f, r = s.send_command(rev_cmd)
    assert f.success
    result_lines = r.str_result.split("\r\n")
    assert result_lines[0] == "SIMCOM_Ltd"
    assert result_lines[1].startswith("SIMCOM_SIM")
    assert result_lines[2].startswith("Revision:")

def test_imei(sim800):
    s = SIM800('/dev/ttyAMA0', timeout=3)
    rev_cmd = Command("+GSN", ['8626'])
    f, r = s.send_command(rev_cmd)
    assert f.success
    assert r.str_result.startswith("86264303")

