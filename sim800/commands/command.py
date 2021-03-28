from sim800.results import Result


class Command:
    PREFIX = "AT"
    SUFFIX = "\r"

    def __init__(self, cmd_string="", result_prefixes=None):
        self.cmd = cmd_string
        if result_prefixes is None:
            result_prefixes = []
        self.result_prefixes = list(result_prefixes)

    def __bytes__(self):
        return (self.PREFIX + self.cmd + self.SUFFIX).encode('ascii')

    def __repr__(self):
        return '<{} "{}">'.format(self.__class__.__name__, self.PREFIX + self.cmd)

    def parse_response(self, lines):
        for line in lines:
            s = line.strip()
            for prefix in self.result_prefixes:
                if s.startswith(prefix.encode('ascii')):
                    return Result(line)
        return None

