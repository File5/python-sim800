class Command:
    PREFIX = "AT"

    def __init__(self, cmd_string="", result_prefixes=None):
        self.cmd = cmd_string
        if result_prefixes is None:
            result_prefixes = []
        self.result_prefixes = list(result_prefixes)

    def __bytes__(self):
        return self.cmd.encode('ascii')

    def __repr__(self):
        return '<Command "{}">'.format(self.PREFIX + self.cmd)

    def parse_lines(self, lines):
        parsed_indexes = []
        for i, line in enumerate(lines):
            if line.startswith("AT"):
                pass  # that's just an echo of the sent command
            elif line.startswith("OK") or line.startswith("ERROR"):
                # if i != 0 and lines[i - 1].isspace():
                #     parsed_indexes.append(i - 1)  # empty line before final result
                parsed_indexes.append(i)  # final result
            else:
                for prefix in self.result_prefixes:
                    if line.startswith(prefix):
                        parsed_indexes.append(i)
                        break
        result = []
        for i in parsed_indexes:
            result.append(lines[i])
        for i in reversed(parsed_indexes):
            del lines[i]
        return result

