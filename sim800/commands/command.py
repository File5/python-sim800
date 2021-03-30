import functools
from sim800.results.result import Result, CombinedResult


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


class NextLineArgCommand(ExtendedCommand):
    SUB = "\x1a"  # Ctrl-Z
    ESC = "\x1b"

    @classmethod
    def write(cls, *args, next_line_arg=""):
        if cls.WRITE not in cls.COMMANDS:
            raise NotImplementedError
        params = [cls.LEFT_OUT if x is None else x for x in args]
        params = ['"{}"'.format(x) if isinstance(x, str) else str(x) for x in params]
        cmd_string_suffix = "=" + ','.join(params)

        cmd_string = cls.BASE_CMD + cmd_string_suffix + "\r" + next_line_arg + cls.SUB
        result_prefixes = [cls.BASE_CMD + ': ']

        cmd = cls(cmd_string, result_prefixes)
        cmd.SUFFIX = ""
        return cmd


class CombinedCommand(Command):
    def __init__(self, commands, *args):
        if len(args) > 0:
            # agruments are passed as arg1, arg2, ...
            self.commands = [commands] + list(args)
        else:
            try:
                # arguments are passed as iterable(arg1, arg2, ...)
                self.commands = list(commands)
            except TypeError:
                # it's single argument arg1
                self.commands = [commands]

        cmd_string = [c.cmd for c in self.commands]
        cmd_string = ";".join(cmd_string)
        result_prefixes = [c.result_prefixes for c in self.commands]
        result_prefixes = functools.reduce(lambda a, b: a + b, result_prefixes, [])
        super().__init__(cmd_string, result_prefixes)

    def parse_response(self, lines):
        results = []
        for line in lines:
            s = line.strip()
            for cmd in self.commands:
                result = cmd.parse_response([line])
                if result is not None:
                    results.append(result)
                    break  # cmd loop
        if len(results) > 0:
            return CombinedResult(results)
        else:
            return None

