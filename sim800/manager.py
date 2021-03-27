import serial


class SIM800:
    def __init__(self, *args, **kwargs):
        self.serial = serial.Serial(*args, **kwargs)

    def close(self):
        self.serial.close()

    def send_command(command: Command):
        pass

