from sim800.results.unsolicited import from_response, NewMessageResult


def test_no_unsolicited():
    r = [
        b'AT+COPS?\r',
        b'\r\n+COPS: 0,0,"CHINA MOBILE"\r\n',
        b'\r\nOK\r\n',
    ]
    results = from_response(r)
    assert len(results) == 0

def test_cmti():
    r = [
        b'\r\n+CMTI: "ME",1\r\n'
    ]
    results = from_response(r)
    assert len(results) == 1

    result = results[0]
    assert result.memory == "ME"
    assert result.index == 1
    assert not result.mms
    assert type(result.index) is int

def test_cmti_mms():
    r = [
        b'\r\n+CMTI: "ME",2,"MMS PUSH"\r\n'
    ]
    results = from_response(r)
    assert len(results) == 1

    result = results[0]
    assert result.memory == "ME"
    assert result.index == 2
    assert result.mms
    assert type(result.index) is int

