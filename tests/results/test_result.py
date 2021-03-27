from sim800.results.result import Result


def test_result_repr():
    r = Result(b'\r\nresult\r\n')
    assert repr(r) == '<Result "result">'

def test_result_repr_subclass():
    class DerivedResult(Result):
        pass
    r = DerivedResult(b'\r\nresult\r\n')
    assert repr(r) == '<DerivedResult "result">'

