import pytest

from sim800.commands.command import Command, ExtendedCommand


def test_command_result_prefixes():
    test_cmd = "test_cmd"

    c = Command(test_cmd)
    assert c.result_prefixes == []

    c = Command(test_cmd, [test_cmd])
    assert c.result_prefixes == [test_cmd]

def test_command_bytes():
    test_cmd = "test_cmd"
    c = Command(test_cmd)
    assert bytes(c) == ("AT" + test_cmd + "\r").encode('ascii')

def test_command_repr():
    test_cmd = "test_cmd"
    c = Command(test_cmd)
    assert repr(c) == '<Command "ATtest_cmd">'

def test_command_repr_subclass():
    class DerivedCommand(Command):
        pass
    test_cmd = "test_cmd"
    c = DerivedCommand(test_cmd)
    assert repr(c) == '<DerivedCommand "ATtest_cmd">'

def test_command_parse_lines():
    test_cmd = "+COPS"
    c = Command(test_cmd, [test_cmd])
    r = [
        b'\r\n+CNMI\r\n',  # some unsolicited result
        b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n',
        b'\r\nOK\r\n',
    ]
    cmd_r = c.parse_response(r)

    assert cmd_r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

def test_command_parse_lines_wrong():
    test_cmd = "+COPS"
    c = Command(test_cmd, [test_cmd])
    r = [
        b'\r\n+CNMI: 1,1\r\n',
    ]
    cmd_r = c.parse_response(r)

    assert cmd_r is None

def test_command_parse_lines_no_empty_before():
    test_cmd = "+COPS"
    c = Command(test_cmd, [test_cmd])
    r = [
        b'AT+COPS?\r',
        b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n',
        b'\r\nOK\r\n',
    ]
    cmd_r = c.parse_response(r)

    assert cmd_r.raw_result == b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n'

def test_command_parse_lines_no_prefix_crlf():
    test_cmd = "+COPS"
    c = Command(test_cmd, [test_cmd])
    r = [
        b'+COPS: 0,0,"CHINA MOBILE"\r\n',
    ]
    cmd_r = c.parse_response(r)

    assert cmd_r.raw_result == b'+COPS: 0,0,"CHINA MOBILE"\r\n'

def test_extended_command_all():
    class TestCommand(ExtendedCommand):
        BASE_CMD = "+TEST"

    c = TestCommand.test()
    assert bytes(c) == b'AT+TEST=?\r'
    assert c.result_prefixes == ['+TEST: ']

    c = TestCommand.read()
    assert bytes(c) == b'AT+TEST?\r'
    assert c.result_prefixes == ['+TEST: ']

    c = TestCommand.write(1, "arg2", 3)
    assert bytes(c) == b'AT+TEST=1,"arg2",3\r'
    assert c.result_prefixes == ['+TEST: ']

    c = TestCommand.execute()
    assert bytes(c) == b'AT+TEST\r'
    assert c.result_prefixes == ['+TEST: ']

def test_extended_command_test_read_write():
    class TestCommand(ExtendedCommand):
        BASE_CMD = "+TEST"
        COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]

    c = TestCommand.test()
    assert bytes(c) == b'AT+TEST=?\r'
    assert c.result_prefixes == ['+TEST: ']

    c = TestCommand.read()
    assert bytes(c) == b'AT+TEST?\r'
    assert c.result_prefixes == ['+TEST: ']

    c = TestCommand.write(1, "arg2", 3)
    assert bytes(c) == b'AT+TEST=1,"arg2",3\r'
    assert c.result_prefixes == ['+TEST: ']

    with pytest.raises(NotImplementedError):
        c = TestCommand.execute()

def test_extended_command_write_params():
    class TestCommand(ExtendedCommand):
        BASE_CMD = "+TEST"

    c = TestCommand.write(TestCommand.LEFT_OUT, 1, "arg2", 3)
    assert bytes(c) == b'AT+TEST=,1,"arg2",3\r'
    assert c.result_prefixes == ['+TEST: ']

    c = TestCommand.write(TestCommand.LEFT_OUT, None, 2, TestCommand.LEFT_OUT)
    assert bytes(c) == b'AT+TEST=,,2,\r'
    assert c.result_prefixes == ['+TEST: ']

