from sim800.results.result import Result

class UnsolicitedResult(Result):
    pass


class NewMessageResult(UnsolicitedResult):
    PREFIX = b'+CMTI: '
    PREFIXES = [PREFIX]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        params = self.str_result[len(self.PREFIX):].split(",")
        assert len(params) >= 2
        self.memory = params[0].strip(' "')
        self.index = int(params[1].strip())
        self.mms = False
        if len(params) > 2:
            mms_push = params[2].strip(' "')
            self.mms = mms_push == "MMS PUSH"


FACTORIES = [
    NewMessageResult.from_response
]

def from_response(response):
    results = []
    for line in response:
        for factory in FACTORIES:
            r = factory(line)
            if r is not None:
                results.append(r)
                break  # factories loop
    return results

