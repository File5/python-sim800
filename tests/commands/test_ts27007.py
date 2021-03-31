import pytest

import datetime

from sim800.commands.ts27007 import *


def test_select_charset_command():
    c = SelectCharSetCommand.write(SelectCharSetCommand.GSM)
    assert bytes(c) == b'AT+CSCS="GSM"\r'

    c = SelectCharSetCommand.write(SelectCharSetCommand.UCS2)
    assert bytes(c) == b'AT+CSCS="UCS2"\r'

    c = SelectCharSetCommand.write(SelectCharSetCommand.UCS2)
    assert bytes(c) == b'AT+CSCS="UCS2"\r'

    with pytest.raises(ValueError):
        c = SelectCharSetCommand.write("NOT_SUPPORTED")


def test_select_type_of_address_command():
    c = SelectTypeOfAddressCommand.write(SelectTypeOfAddressCommand.INTERNATIONAL)
    assert bytes(c) == b'AT+CSTA=145\r'

    with pytest.raises(ValueError):
        c = SelectTypeOfAddressCommand.write(999)


def test_imsi_command_write(sim800):
    c = IMSICommand.execute()
    sim800.serial.after_next_write(b'\r\n9999\r\n\r\nOK\r\n')
    f, r = sim800.send_command(c)

    assert f.success
    assert r.str_result == "9999"


def test_clip_command_write(sim800):
    c = CallingLineIdPresentationCommand.write(True)
    assert bytes(c) == b'AT+CLIP=1\r'

    c = CallingLineIdPresentationCommand.write(False)
    assert bytes(c) == b'AT+CLIP=0\r'


def test_select_phonebook_memory_storage_command_write():
    c = SelectPhonebookMemoryStorageCommand.write(SelectPhonebookMemoryStorageCommand.SIM)
    assert bytes(c) == b'AT+CPBS="SM"\r'

    with pytest.raises(ValueError):
        c = SelectPhonebookMemoryStorageCommand.write("NOT_SUPPORTED")


def test_write_phonebook_entry_command_encode_text():
    text = WritePhonebookEntryCommand.encode_text('Test\\ "text"', "GSM")
    assert text == 'Test\\5C \\22text\\22'


def test_enter_pin_command_write():
    c = EnterPINCommand.write("1234")
    assert bytes(c) == b'AT+CPIN="1234"\r'

    with pytest.raises(AssertionError):
        c = EnterPINCommand.write(1234)


def test_clock_command_write():
    dt = datetime.datetime(year=2021, month=3, day=3, hour=8, minute=5, second=3)
    tz = datetime.timedelta(hours=2)
    c = ClockCommand.write(dt, tz)

    assert bytes(c) == b'AT+CCLK="21/03/03,08:05:03+08"\r'

    tz = datetime.timedelta(hours=-11, minutes=-45)
    c = ClockCommand.write(dt, tz)

    assert bytes(c) == b'AT+CCLK="21/03/03,08:05:03-47"\r'

    tz = datetime.timedelta(hours=12)
    c = ClockCommand.write(dt, tz)

    assert bytes(c) == b'AT+CCLK="21/03/03,08:05:03+48"\r'

