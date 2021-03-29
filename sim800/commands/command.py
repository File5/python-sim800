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


class NoResponseCommand(Command):
    def parse_response(self, lines):
        return None


class ExtendedCommand(Command):
    TEST = 'TEST'
    READ = 'READ'
    WRITE = 'WRITE'
    EXECUTE = 'EXECUTE'
    COMMANDS = [TEST, READ, WRITE, EXECUTE]

    BASE_CMD = ""

    class _LeftOut:
        def __str__(self):
            return ''
    LEFT_OUT = _LeftOut()

    @classmethod
    def _factory(cls, cmd_string_suffix, *args, **kwargs):
        cmd_string = cls.BASE_CMD + cmd_string_suffix
        result_prefixes = [cls.BASE_CMD + ': ']
        return cls(cmd_string, result_prefixes, *args, **kwargs)

    @classmethod
    def test(cls, *args, **kwargs):
        if cls.TEST not in cls.COMMANDS:
            raise NotImplementedError
        return cls._factory("=?", *args, **kwargs)

    @classmethod
    def read(cls, *args, **kwargs):
        if cls.READ not in cls.COMMANDS:
            raise NotImplementedError
        return cls._factory("?", *args, **kwargs)

    @classmethod
    def write(cls, *args, **kwargs):
        if cls.WRITE not in cls.COMMANDS:
            raise NotImplementedError
        params = [cls.LEFT_OUT if x is None else x for x in args]
        params = ['"{}"'.format(x) if isinstance(x, str) else str(x) for x in params]
        cmd_string_suffix = "=" + ','.join(params)
        return cls._factory(cmd_string_suffix, **kwargs)

    @classmethod
    def execute(cls, *args, **kwargs):
        if cls.EXECUTE not in cls.COMMANDS:
            raise NotImplementedError
        return cls._factory("", *args, **kwargs)

