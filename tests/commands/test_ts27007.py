import datetime

from sim800.commands.ts27007 import *


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

