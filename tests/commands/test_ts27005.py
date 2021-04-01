import pytest

from sim800.commands.ts27005 import *


def test_delete_sms_message_command_write():
    cmd = DeleteSMSMessageCommand

    c = cmd.write(9)
    assert bytes(c) == b'AT+CMGD=9,0\r'

    c = cmd.write(8, cmd.DELETE_READ)
    assert bytes(c) == b'AT+CMGD=8,1\r'

    c = cmd.write(7, cmd.DELETE_READ_SENT)
    assert bytes(c) == b'AT+CMGD=7,2\r'

    c = cmd.write(6, cmd.DELETE_READ_SENT_UNSENT)
    assert bytes(c) == b'AT+CMGD=6,3\r'

    c = cmd.write(5, cmd.DELETE_ALL)
    assert bytes(c) == b'AT+CMGD=5,4\r'

    with pytest.raises(ValueError):
        c = cmd.write(9, 5)

    with pytest.raises(ValueError):
        c = cmd.write("9")


def test_select_sms_message_format_command_write():
    cmd = SelectSMSMessageFormatCommand

    c = cmd.write()
    assert bytes(c) == b'AT+CMGF=0\r'

    c = cmd.write(cmd.TEXT)
    assert bytes(c) == b'AT+CMGF=1\r'

    with pytest.raises(ValueError):
        c = cmd.write(2)


def test_list_sms_messages_command_write():
    cmd = ListSMSMessagesCommand

    c = cmd.write(cmd.PDU_MODE.SENT, cmd.PDU_MODE.NOT_CHANGE_STATUS)
    assert bytes(c) == b'AT+CMGL=3,1\r'

    c = cmd.write(cmd.TEXT_MODE.READ, cmd.TEXT_MODE.NORMAL)
    assert bytes(c) == b'AT+CMGL="REC READ",0\r'

    c = cmd.write(cmd.PDU_MODE.UNREAD)
    assert bytes(c) == b'AT+CMGL=0,0\r'

    c = cmd.write(cmd.TEXT_MODE.ALL)
    assert bytes(c) == b'AT+CMGL="ALL",0\r'

    with pytest.raises(ValueError):
        c = cmd.write("NOT_SUPPORTED", cmd.TEXT_MODE.NORMAL)

    with pytest.raises(ValueError):
        c = cmd.write(5, cmd.TEXT_MODE.NORMAL)

    with pytest.raises(ValueError):
        c = cmd.write(cmd.TEXT_MODE.READ, 3)


def test_read_sms_message_command_write():
    cmd = ReadSMSMessageCommand

    c = cmd.write(9)
    assert bytes(c) == b'AT+CMGR=9,0\r'

    c = cmd.write(8, cmd.NOT_CHANGE_STATUS)
    assert bytes(c) == b'AT+CMGR=8,1\r'

    with pytest.raises(ValueError):
        c = cmd.write(9, 2)

    with pytest.raises(ValueError):
        c = cmd.write("9")


def test_send_sms_message_command_write():
    cmd = SendSMSMessageCommand

    c = cmd.write("+999", 145, text="Test SMS message")
    assert bytes(c) == b'AT+CMGS="+999",145\rTest SMS message\x1a'

    c = cmd.write("+999", text="Test SMS message")
    assert bytes(c) == b'AT+CMGS="+999"\rTest SMS message\x1a'

    c = cmd.write(24, pdu="001100039199F90000FF10D4F29C0E9A36A7A076793E0F9FCB")
    assert bytes(c) == b'AT+CMGS=24\r001100039199F90000FF10D4F29C0E9A36A7A076793E0F9FCB\x1a'


def test_write_sms_message_to_memory_command_write():
    cmd = WriteSMSMessageToMemoryCommand

    c = cmd.write("+999", 145, cmd.TEXT_MODE.UNSENT, text="Test SMS message")
    assert bytes(c) == b'AT+CMGW="+999",145,"STO UNSENT"\rTest SMS message\x1a'

    c = cmd.write(24, cmd.PDU_MODE.SENT, pdu="001100039199F90000FF10D4F29C0E9A36A7A076793E0F9FCB")
    assert bytes(c) == b'AT+CMGW=24,3\r001100039199F90000FF10D4F29C0E9A36A7A076793E0F9FCB\x1a'

    c = cmd.write("+999", 145, cmd.TEXT_MODE.SENT, text="Test SMS message")
    assert bytes(c) == b'AT+CMGW="+999",145,"STO SENT"\rTest SMS message\x1a'

    c = cmd.write(24, cmd.PDU_MODE.UNREAD, pdu="001100039199F90000FF10D4F29C0E9A36A7A076793E0F9FCB")
    assert bytes(c) == b'AT+CMGW=24,0\r001100039199F90000FF10D4F29C0E9A36A7A076793E0F9FCB\x1a'


def test_cnd_sms_message_from_storage_command_write():
    cmd = SendSMSMessageFromStorageCommand

    c = cmd.write(9,"+999",145)
    assert bytes(c) == b'AT+CMSS=9,"+999",145\r'

    c = cmd.write(9,"+999")
    assert bytes(c) == b'AT+CMSS=9,"+999"\r'

    c = cmd.write(9)
    assert bytes(c) == b'AT+CMSS=9\r'

    with pytest.raises(ValueError):
        c = cmd.write("9","+999",145)

    with pytest.raises(ValueError):
        c = cmd.write(9,999,145)

    with pytest.raises(ValueError):
        c = cmd.write(9,"+999","145")


def test_new_sms_message_indication_command_write():
    cmd = NewSMSMessageIndicationCommand


