import io
import serial


class TimeoutException(Exception):
    pass


class SIM800:
    DEFAULT_TIMEOUT = 5  # (float) seconds
    DEFAULT_WRITE_TIMEOUT = 5  # (float) seconds

    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = DEFAULT_TIMEOUT
        if 'write_timeout' not in kwargs:
            kwargs['write_timeout'] = DEFAULT_WRITE_TIMEOUT
        self.serial = serial.Serial(*args, **kwargs)
        self.unsolicited = []

    def close(self):
        self.serial.close()

    def send_command(command: Command, recv_result=True):
        try:
            self.serial.write(bytes(command))

            if recv_result:
                return self.recv_command_result()

        except (serial.SerialTimeoutException, TimeoutException) as e:
            raise TimeoutException(e)

    def recv_unsolicited(self):
        if len(self.unsolicited) > 0:
            return self.unsolicited.pop(0)

        line = self.serial.read_until(b'\r\n')
        if line == b'':
            raise TimeoutException('read timeout')
        # TODO: parse unsolicited
        return None

    def recv_command_result(self):
        response = io.BytesIO()

        line = self.serial.read_until(b'\r\n')
        if line == b'':
            raise TimeoutException('read timeout')
        response.write(line)
        final = ExecutedCommandFinalResult.from_response(line)
        while final is None:
            line = self.serial.read_until(b'\r\n')
            if line == b'':
                raise TimeoutException('read timeout')
            response.write(line)
            final = ExecutedCommandFinalResult.from_response(line)

        # TODO: parse unsolicited
        if final.success:
            return command.parse_response(response)
        else:
            return final


