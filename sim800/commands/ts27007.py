import datetime
from sim800.commands.command import Command, NoResponseCommand, ExtendedCommand
from sim800.results import Result


class SelectCharSetCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CSCS"

    GSM = "GSM"
    UCS2 = "UCS2"
    IRA = "IRA"
    HEX = "HEX"
    PCCP = "PCCP"
    PCDN = "PCDN"
    LATIN1 = "8859-1"

    CHSET = [GSM, UCS2, IRA, HEX, PCCP, PCDN, LATIN1]

    @classmethod
    def write(cls, chset):
        if chset not in cls.CHSET:
            raise ValueError('"{}" is not supported'.format(chset))
        return super().write(chset)


class SelectTypeOfAddressCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CSTA"

    UNKNOWN = 129
    NATIONAL = 161
    INTERNATIONAL = 145
    NETWORK = 177

    TYPE = [UNKNOWN, NATIONAL, INTERNATIONAL, NETWORK]

    @classmethod
    def write(cls, t):
        if t not in cls.TYPE:
            raise ValueError('"{}" is not supported'.format(t))
        return super().write(t)


class IMSICommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.EXECUTE]
    BASE_CMD = "+CIMI"

    def __init__(self, cmd_string, result_prefixes=None):
        result_prefixes = [str(i) for i in range(10) if i not in (1, 8)]
        super().__init__(cmd_string, result_refixes)


class CallingLineIdPresentationCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CLIP"

    @classmethod
    def write(cls, enable=False):
        n = 1 if enable else 0
        return super().write(n)


class OperationSelectionCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+COPS"


class FindPhonebookEntriesCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CPBF"


class ReadCurrentPhonebookEntriesCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CPBR"


class SelectPhonebookMemoryStorageCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CPBS"

    OWN = "ON"
    SIM = "SM"
    MODEM = "ME"
    FIX_DIALING = "FD"

    STORAGE = [OWN, SIM, MODEM, FIX_DIALING]

    @classmethod
    def write(cls, storage=None):
        if storage is None:
            storage = cls.SIM
        if storage not in cls.STORAGE:
            raise ValueError('"{}" is not supported'.format(storage))
        return super().write(storage)


class WritePhonebookEntryCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CPBW"

    NATIONAL = 129  # for some reason it's not 161 here (as stated in the docs)
    INTERNATIONAL = 145

    TYPE = [NATIONAL, INTERNATIONAL]

    @staticmethod
    def encode_text(text, current_chset):
        assert current_chset == "GSM", 'only "GSM" charset is supported now'
        try:
            text.encode('ascii')

            text = text.replace('\\', '\\5C').replace('"', '\\22').replace('\x08', '\\08').replace('\0', '\\00')
            return text
        except UnicodeEncodeError:
            # there are characters out of range(128)
            raise ValueError('text contains non-ASCII characters')


class EnterPINCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CPIN"

    @classmethod
    def write(cls, *args):
        assert all([isinstance(x, str) for x in args]), 'arguments should be strings'
        return super().write(*args)


class NetworkRegistrationCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CREG"

    DISABLE = 0
    ENABLE = 1
    ENABLE_LOC = 2

    N = [DISABLE, ENABLE, ENABLE_LOC]

    @classmethod
    def write(cls, n=None):
        if n is None:
            n = cls.DISABLE
        if n not in cls.N:
            raise ValueError('"{}" is not supported'.format(n))
        return super().write(n)


class SignalQualityReportCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.EXECUTE]
    BASE_CMD = "+CSQ"


class ClockCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CCLK"

    DATETIME_FORMAT = '%y/%m/%d,%H:%M:%S'
    TZ_FORMAT = '{:+03}'
    QUARTER = 15 * 60

    @classmethod
    def write(cls, time, tz):
        if isinstance(time, str):
            time_string = time
        elif isinstance(time, datetime.datetime):
            tz_seconds = tz.seconds
            if tz.days < 0:
                tz_seconds -= 86400
            tz_value = tz_seconds // cls.QUARTER
            time_string = time.strftime(cls.DATETIME_FORMAT) + cls.TZ_FORMAT.format(tz_value)
        else:
            raise ValueError("unsupported argument type, only 'str' and 'datetime' are supported")
        return super().write(time_string)


class BatteryChargeCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.EXECUTE]
    BASE_CMD = "+CBC"


class USSDCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CUSD"

    DISABLE_RESULT = 0
    ENABLE_RESULT = 1
    CANCEL_SESSION = 2

    N = [DISABLE_RESULT, ENABLE_RESULT, CANCEL_SESSION]

