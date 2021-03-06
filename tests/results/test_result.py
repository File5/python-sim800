from sim800.results.result import Result, ExecutedCommandFinalResult, CombinedResult


def test_result_repr():
    r = Result(b'\r\nresult\r\n')
    assert repr(r) == '<Result "result">'

def test_result_repr_subclass():
    class DerivedResult(Result):
        pass
    r = DerivedResult(b'\r\nresult\r\n')
    assert repr(r) == '<DerivedResult "result">'

def test_result_str_result():
    r = Result(b'\r\nresult\r\n')
    assert r.str_result == "result"

def test_executed_command_final_result():
    response = b'\r\nOK\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert r.success
    assert r.error is None
    assert repr(r) == '<ExecutedCommandFinalResult "OK">'

def test_executed_command_final_result_from_not_final():
    response = b'\r\nSIM800 R14.18\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert r is None

def test_executed_command_final_result_error():
    response = b'\r\nERROR\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert not r.success
    assert r.error == 'ERROR'
    assert repr(r) == '<ExecutedCommandFinalResult "ERROR">'

def test_executed_command_final_result_cme():
    response = b'\r\n+CME ERROR: SIM not inserted\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert not r.success
    assert r.error == 'SIM not inserted'
    assert repr(r) == '<ExecutedCommandFinalResult "+CME ERROR: SIM not inserted">'

def test_executed_command_final_result_cme_code():
    response = b'\r\n+CME ERROR: 10\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert not r.success
    assert r.error == 'SIM not inserted'
    assert repr(r) == '<ExecutedCommandFinalResult "+CME ERROR: 10">'

def test_executed_command_final_result_cms():
    response = b'\r\n+CMS ERROR: Unknown\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert not r.success
    assert r.error == 'Unknown'
    assert repr(r) == '<ExecutedCommandFinalResult "+CMS ERROR: Unknown">'

def test_executed_command_final_result_cms_code():
    response = b'\r\n+CMS ERROR: 500\r\n'
    r = ExecutedCommandFinalResult.from_response(response)

    assert not r.success
    assert r.error == 'Unknown'
    assert repr(r) == '<ExecutedCommandFinalResult "+CMS ERROR: 500">'

def test_combined_result():
    results = [Result(b'\r\n1\r\n'), Result(b'\r\n2\r\n'), Result(b'\r\n3\r\n')]
    r = CombinedResult(results)

    assert r.raw_result == b'\r\n1\r\n\r\n2\r\n\r\n3\r\n'
    assert repr(r) == '<CombinedResult [1, 2, 3]>'
    assert r.str_result == '[1, 2, 3]'

