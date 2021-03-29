import io
import serial
from sim800.commands.command import Command
from sim800.results.result import ExecutedCommandFinalResult
import sim800.results.unsolicited as unsolicited


class TimeoutException(Exception):
    pass


class SIM800:
    DEFAULT_TIMEOUT = 5  # (float) seconds
    DEFAULT_WRITE_TIMEOUT = 5  # (float) seconds

    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.DEFAULT_TIMEOUT
        if 'write_timeout' not in kwargs:
            kwargs['write_timeout'] = self.DEFAULT_WRITE_TIMEOUT
        self.serial = serial.Serial(*args, **kwargs)
        self.unsolicited = []
        self.__readline_buffer = b''
        self.__cached_line = b''

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
            raise TimeoutException(e)

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
        line = self.__readline_buffer
        self.__readline_buffer = b''

        stream = self.serial
        if not line.endswith(b'\r'):
            line += stream.read_until(b'\r')

        if len(line) < 1:
            raise TimeoutException('read timeout')
            #return line  # b''
        if not line.endswith(b'\r'):
            return line

        # try to read b'\n'
        next_b = stream.read(1)
        if next_b.startswith(b'\n'):
            line += next_b
        else:
            self.__readline_buffer += next_b

        return line

    def _readline_or_cached(self):
        if len(self.__cached_line) > 0:
            line = self.__cached_line
            self.__cached_line = b''
        else:
            line = self.readline()
        return line

    def read_echo_or_result(self):
        stream = self.serial
        line = self._readline_or_cached()

        if line.endswith(b'\r'):
            return line  # it's command + b'\r'
        if line == b'\r\n':
            # it's result start
            result = io.BytesIO(line)
            result.seek(0, io.SEEK_END)
            while True:
                try:
                    line = self._readline_or_cached()
                except TimeoutException:
                    return result.getvalue()

                if not line.endswith(b'\r\n'):
                    # something's wrong, result continuation should end with \r\n
                    # e.g. it's unsolicited before command
                    self.__cached_line = line
                    return result.getvalue()

                result.write(line)

                try:
                    self.__cached_line = self.readline()
                except TimeoutException:
                    self.__cached_line = b''

                if len(self.__cached_line) < 1 or self.__cached_line.startswith(b'\r\n'):
                    # it's result end
                    return result.getvalue()

