class Result:
    def __init__(self, raw_result):
        self.raw_result = raw_result

    def __repr__(self):
        str_result = self.raw_result.decode('ascii').strip()
        return '<{} "{}">'.format(self.__class__.__name__, str_result)

