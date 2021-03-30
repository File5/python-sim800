class Result:
    PREFIXES = []

    def __init__(self, raw_result):
        self.raw_result = raw_result

    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self.str_result)

    def __eq__(self, other):
        return self.raw_result == other.raw_result

    @property
    def str_result(self):
        return self.raw_result.decode('ascii').strip()

    @classmethod
    def from_response(cls, response):
        s = response.strip()
        for prefix in cls.PREFIXES:
            if s.startswith(prefix):
                return cls(response)
        return None


class ExecutedCommandFinalResult(Result):
    OK_PREFIX = "OK"
    ERROR_PREFIX = "ERROR"
    CME_ERROR_PREFIX = "+CME ERROR: "
    CMS_ERROR_PREFIX = "+CMS ERROR: "
    PREFIXES = [x.encode('ascii') for x in (OK_PREFIX, ERROR_PREFIX, CME_ERROR_PREFIX, CMS_ERROR_PREFIX)]

    CME_CODE_TO_MEANING = {
        0: 'phone failure',
        10: 'SIM not inserted',
        100: 'unknown',
        # add other CME ERROR codes from SIM800 Series command manual
    }
    CMS_CODE_TO_MEANING = {
        500: 'Unknown',
        # add CMS ERROR codes from SIM800 Series command manual
    }

    def __init__(self, raw_result):
        super().__init__(raw_result)
        self.error = None

        s = self.str_result

        if s.startswith(self.ERROR_PREFIX):
            self.error = 'ERROR'

        elif s.startswith(self.CME_ERROR_PREFIX):
            err = s[len(self.CME_ERROR_PREFIX):]

            if err.isdigit():
                self.error = self.decode_cme_error_code(err)
            else:
                self.error = err

        elif s.startswith(self.CMS_ERROR_PREFIX):
            err = s[len(self.CMS_ERROR_PREFIX):]

            if err.isdigit():
                self.error = self.decode_cms_error_code(err)
            else:
                self.error = err

        elif not s.startswith(self.OK_PREFIX):
            self.error = 'Unknown response prefix: "{}"'.format(s)

    @property
    def success(self):
        return self.error is None

    @classmethod
    def decode_cme_error_code(cls, err):
        if type(err) is str:
            err = int(err)

        return cls.CME_CODE_TO_MEANING.get(err, 'unknown CME error code')

    @classmethod
    def decode_cms_error_code(cls, err):
        if type(err) is str:
            err = int(err)

        return cls.CMS_CODE_TO_MEANING.get(err, 'unknown CMS error code')


class CombinedResult(Result, list):
    def __init__(self, results):
        raw_result = b''.join([r.raw_result for r in results])
        Result.__init__(self, raw_result)
        list.__init__(self, results)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.str_result)

    @property
    def str_result(self):
        return '[' + ', '.join([r.str_result for r in self]) + ']'

