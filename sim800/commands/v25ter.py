from sim800.commands.command import Command, NoResponseCommand, ExtendedCommand
from sim800.results import Result


class ATCommand(NoResponseCommand):
    def __init__(self):
        super().__init__("")


class SetEchoCommand(NoResponseCommand):
    def __init__(self, enabled=True):
        cmd_string = "E1" if enabled else "E0"
        super().__init__(cmd_string)


class DisplayProductInfoCommand(Command):
    def __init__(self):
        super().__init__("I", ['SIM'])


class FactoryDefinedConfigCommand(NoResponseCommand):
    def __init__(self):
        super().__init__("&F")


class DisplayCurrentConfigCommand(NoResponseCommand):
    def __init__(self):
        super().__init__("&V")

    def parse_response(self, lines):
        return Result(b''.join(lines))


class StoreActiveConfigCommand(NoResponseCommand):
    def __init__(self):
        super().__init__("&W")


class ListTACapabilitiesCommand(Command):
    def __init__(self):
        super().__init__("+GCAP", ['+GCAP: '])


class ManufacturerInfoCommand(Command):
    def __init__(self):
        super().__init__("+GMI", ['SIM'])


class ModelInfoCommand(Command):
    def __init__(self):
        super().__init__("+GMM", [''])


class TARevisionInfoCommand(Command):
    def __init__(self):
        super().__init__("+GMR", ['Revision: '])


class GlobalObjectIdCommand(Command):
    def __init__(self):
        super().__init__("+GOI", [''])  # prefix '{' ?


class ImeiCommand(Command):
    def __init__(self):
        super().__init__("+GSN", ['86264303'])


class ControlCharFramingCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+ICF"


class LocalDataFlowControlCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+IFC"


class FixedLocalRateCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+IPR"

