from sim800.commands.command import Command


def test_command_bytes():
    test_cmd = "test_cmd"
    c = Command(test_cmd)
    assert bytes(c) == test_cmd.encode('ascii')

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
        b'',
        b'+CNMI',  # some unsolicited result
        b'',
        b'+COPS: 0,0,"CHINA MOBILE"',
        b'',
        b'OK',
        b''
    ]
    r = b'\r\n'.join(r)
    cmd_r = c.parse_response(r)

    assert cmd_r.raw_result == [
        b'',
        b'+COPS: 0,0,"CHINA MOBILE"',
        b'',
    ]

