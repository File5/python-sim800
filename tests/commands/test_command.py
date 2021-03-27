from sim800.commands.command import Command


def test_command_bytes():
    test_cmd = "test_cmd"
    c = Command(test_cmd)
    assert bytes(c) == test_cmd.encode('ascii')

def test_command_repr():
    test_cmd = "test_cmd"
    c = Command(test_cmd)
    assert repr(c) == '<Command "ATtest_cmd">'

def test_command_parse_lines():
    test_cmd = "+COPS"
    c = Command(test_cmd, [test_cmd])
    r = [
        "+CNMI\r\n",  # some unsolicited result
        "\r\n",
        '+COPS: 0,0,"CHINA MOBILE"\r\n',
        "\r\n",
        "OK\r\n"
    ]
    cmd_r = c.parse_lines(r)

    assert cmd_r == [
        '+COPS: 0,0,"CHINA MOBILE"\r\n',
        "OK\r\n"
    ]
    assert r == [
        "+CNMI\r\n",  # some unsolicited result
        "\r\n",
        "\r\n",
    ]

