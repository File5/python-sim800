import io
import serial
from sim800.commands.command import Command
from sim800.results.result import ExecutedCommandFinalResult
import sim800.results.unsolicited as unsolicited


class TimeoutException(Exception):
    pass


class BufferedReader(io.BufferedReader):
    def __init__(self, *args, **kwargs):
        self._timeout = 1
        if 'timeout' in kwargs:
            self._timeout = kwargs.pop('timeout')
        super().__init__(*args, **kwargs)

    def read_until(self, expected=b'\n', size=None):
        lenterm = len(expected)
        line = bytearray()
        timeout = serial.serialutil.Timeout(self._timeout)
        while True:
            c = self.read(1)
            if c:
                line += c
                if line[-lenterm:] == expected:
                    break
                if size is not None and len(line) >= size:
                    break
            else:
                break
            if timeout.expired():
                break
        return bytes(line)


class SIM800:
    DEFAULT_TIMEOUT = 5  # (float) seconds
    DEFAULT_WRITE_TIMEOUT = 5  # (float) seconds

    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT
        if 'write_timeout' not in kwargs:
            kwargs['write_timeout'] = self.DEFAULT_WRITE_TIMEOUT
        self.serial = serial.Serial(*args, **kwargs)
        self.buffered_reader = BufferedReader(self.serial, timeout=kwargs['timeout'])
        self.unsolicited = []

    def close(self):
        self.serial.close()

    def send_command(self, command: Command, recv_result=True):
        try:
            self.serial.write(bytes(command))

            if recv_result:
                return self.recv_command_result(command)

        except (serial.SerialTimeoutException, TimeoutException) as e:
            raise TimeoutException(e)

    def recv_unsolicited(self):
        if len(self.unsolicited) > 0:
            return self.unsolicited.pop(0)

        try:
            line = self.read_echo_or_result()
            results = unsolicited.from_response([line])
            if len(results) >= 1:
                return results[0]
            else:
                return None
        except (serial.SerialTimeoutException, TimeoutException) as e:
            return None

    def recv_command_result(self, command: Command):
        lines = []

        try:
            line = self.read_echo_or_result()
            lines.append(line)

            final = ExecutedCommandFinalResult.from_response(line)
            while final is None:
                line = self.read_echo_or_result()
                lines.append(line)

                final = ExecutedCommandFinalResult.from_response(line)

            # now, the final result is found but we need to parse previous lines

            unsolicited_results = unsolicited.from_response(lines)
            self.unsolicited += unsolicited_results
            return final, command.parse_response(lines)

        except (serial.SerialTimeoutException, TimeoutException) as e:
            raise TimeoutException(e)

    def readline(self):
        stream = self.buffered_reader
        line = stream.read_until(b'\r')
        next_b = stream.peek(1)
        if next_b.startswith(b'\n'):
            line += stream.read(1)
        return line

    def read_echo_or_result(self):
        stream = self.buffered_reader
        line = self.readline()
        if line.endswith(b'\r'):
            return line  # it's command + b'\r'
        if line == b'\r\n':
            # it's result start
            result = io.BytesIO(line)
            result.seek(0, io.SEEK_END)
            while True:
                line = self.readline()
                if not line.endswith(b'\r\n'):
                    # something's wrong, result continuation should end with \r\n
                    # e.g. it's unsolicited before command
                    # discard line (it's just echo ending with \r)
                    return result.getvalue()

                result.write(line)
                next_b = stream.peek(2)
                if len(next_b) < 1 or next_b.startswith(b'\r\n'):
                    # it's result end
                    return result.getvalue()

