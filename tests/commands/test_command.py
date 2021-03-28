from sim800.commands.command import Command


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

