import pytest

from sim800.manager import TimeoutException
from sim800.results.result import Result
from sim800.commands.simcom import *


def test_power_off_command(sim800, bytes_io):
    cmd = PowerOffCommand(False)
    assert bytes(cmd) == b'AT+CPOWD=0\r'

    cmd = PowerOffCommand()
    assert bytes(cmd) == b'AT+CPOWD=1\r'

    cmd = PowerOffCommand(True)
    assert bytes(cmd) == b'AT+CPOWD=1\r'

    sim800.serial.after_next_write(b'\r\nNORMAL POWER DOWN\r\n')
    sim800.send_command(cmd, recv_result=False)
    with pytest.raises(TimeoutException):
        sim800.recv_command_result(cmd)

    sim800.serial = bytes_io()
    sim800.serial.after_next_write(b'\r\nNORMAL POWER DOWN\r\n')
    sim800.send_command(cmd, recv_result=False)
    r = sim800.read_echo_or_result()  # read echo of sent command
    r = sim800.read_echo_or_result()  # read result
    r = Result(r)

    assert r.str_result == "NORMAL POWER DOWN"


def test_times_remained_to_input_pin_puk_command(sim800):
    cmd = TimesRemainedToInputPINPUKCommand()
    assert bytes(cmd) == b'AT+SPIC\r'

    sim800.serial.after_next_write(b'\r\n+SPIC: 3,3,10,10\r\n\r\nOK\r\n')
    f, r = sim800.send_command(cmd)
    assert f.success
    assert r.str_result == "+SPIC: 3,3,10,10"


def test_delete_all_sms_messages_command_write():
    cmd = DeleteAllSMSMessagesCommand

    c = cmd.write(cmd.TEXT_MODE.READ)
    assert bytes(c) == b'AT+CMGDA="DEL READ"\r'

    c = cmd.write(cmd.TEXT_MODE.RECEIVED)
    assert bytes(c) == b'AT+CMGDA="DEL INBOX"\r'

    c = cmd.write(cmd.TEXT_MODE.ALL)
    assert bytes(c) == b'AT+CMGDA="DEL ALL"\r'

    c = cmd.write(cmd.PDU_MODE.UNREAD)
    assert bytes(c) == b'AT+CMGDA=2\r'

    c = cmd.write(cmd.PDU_MODE.RECEIVED)
    assert bytes(c) == b'AT+CMGDA=5\r'

    c = cmd.write(cmd.PDU_MODE.ALL)
    assert bytes(c) == b'AT+CMGDA=6\r'

    with pytest.raises(ValueError):
        c = cmd.write("NOT_SUPPORTED")

    with pytest.raises(ValueError):
        c = cmd.write(7)


def test_display_product_identification_info_command(sim800):
    cmd = DisplayProductIdentificationInfoCommand()
    assert bytes(cmd) == b'AT+GSV\r'
    sim800.serial.after_next_write(b'\r\nSIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:9999999SIM800L99\r\n\r\nOK\r\n')
    f, r = sim800.send_command(cmd)
    assert f.success
    assert r.str_result == "SIMCOM_Ltd\r\nSIMCOM_SIM800L\r\nRevision:9999999SIM800L99"


def test_reject_incoming_call_command_write():
    cmd = RejectIncomingCallCommand

    c = cmd.write()
    assert bytes(c) == b'AT+GSMBUSY=0\r'

    c = cmd.write(cmd.FORBID_ALL)
    assert bytes(c) == b'AT+GSMBUSY=1\r'

    c = cmd.write(cmd.FORBID_ALL_BUT_CSD)
    assert bytes(c) == b'AT+GSMBUSY=2\r'

