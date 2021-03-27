from sim800.results import Result


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
        return '<{} "{}">'.format(self.__class__.__name__, self.PREFIX + self.cmd)

    def parse_response(self, response):
        start_line_no = 0
        last_line_no = -1

        lines = response.split(b'\r\n')
        for line_no, line in enumerate(lines):
            line_str = line.decode('ascii')
            found_prefix = False
            for prefix in self.result_prefixes:

                # check current line
                if line_str.startswith(prefix):
                    start_line_no = line_no
                    last_line_no = line_no

                    # if there is line before current, take it if it's empty
                    if line_no > 0:
                        prev_line = lines[line_no - 1]
                        if prev_line == b'':
                            start_line_no = line_no - 1

                    # if there is line after current, take it if it's empty
                    if line_no + 1 < len(lines):
                        next_line = lines[line_no + 1]
                        if next_line == b'':
                            last_line_no = line_no + 1

                    found_prefix = True
                    break  # prefix loop
            if found_prefix:
                break  # lines loop

        result = lines[start_line_no:last_line_no + 1]
        for i in range(start_line_no, last_line_no + 1):
            del lines[i]

        result = b'\r\n'.join(result)
        if not result.startswith(b'\r\n'):
            result = b'\r\n' + result
        return Result(result)

