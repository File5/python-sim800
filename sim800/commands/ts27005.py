from sim800.commands.command import Command, NoResponseCommand, ExtendedCommand, NextLineArgCommand
from sim800.results import Result


# TODO: delete, just for reference
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


class DeleteSMSMessageCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CMGD"

    DELETE_SPECIFIED = 0
    DELETE_READ = 1
    DELETE_READ_SENT = 2
    DELETE_READ_SENT_UNSENT = 3
    DELETE_ALL = 4

    DEL_FLAG = [DELETE_SPECIFIED, DELETE_READ, DELETE_READ_SENT, DELETE_READ_SENT_UNSENT, DELETE_ALL]

    @classmethod
    def write(cls, index, del_flag=None):
        if del_flag is None:
            del_flag = DELETE_SPECIFIED
        if type(index) is not int:
            raise ValueError('index should be int')
        if del_flag not in cls.DEL_FLAG:
            raise ValueError('{} is not supported'.format(del_flag))
        return super().write(index, del_flag)


class SelectSMSMessageFormatCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CMGF"

    PDU = 0
    TEXT = 1

    MODE = [PDU, TEXT]

    @classmethod
    def write(cls, mode=None):
        if mode is None:
            mode = cls.PDU
        if mode not in cls.MODE:
            raise ValueError('{} is not supported'.format(mode))
        return super().write(mode)


class ListSMSMessagesCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE, ExtendedCommand.EXECUTE]
    BASE_CMD = "+CMGL"

    class _Mode:
        INT = -1

        NORMAL = 0
        NOT_CHANGE_STATUS = 1

        MODE = [NORMAL, NOT_CHANGE_STATUS]

        def __int__(self):
            return self.INT

    class _PduMode(_Mode):
        INT = 0

        UNREAD = 0
        READ = 1
        UNSENT = 2
        SENT = 3
        ALL = 4

        STAT = [UNREAD, READ, UNSENT, SENT, ALL]

    class _TextMode(_Mode):
        INT = 1

        UNREAD = "REC UNREAD"
        READ = "REC READ"
        UNSENT = "STO UNSENT"
        SENT = "STO SENT"
        ALL = "ALL"

        STAT = [UNREAD, READ, UNSENT, SENT, ALL]

    PDU_MODE = _PduMode()
    TEXT_MODE = _TextMode()

    MODE = [int(PDU_MODE), int(TEXT_MODE)]

    @classmethod
    def write(cls, stat, mode=None):
        if mode is None:
            mode = cls.PDU_MODE.NORMAL  # == TEXT_MODE.NORMAL
        if mode not in cls.PDU_MODE.MODE:  # == TEXT_MODE.MODE
            raise ValueError('"{}" is not supported'.format(mode))
        if stat not in cls.PDU_MODE.STAT + cls.TEXT_MODE.STAT:
            raise ValueError('"{}" is not supported'.format(stat))
        return super().write(stat, mode)


class ReadSMSMessageCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CMGR"

    NORMAL = 0
    NOT_CHANGE_STATUS = 1

    MODE = [NORMAL, NOT_CHANGE_STATUS]

    @classmethod
    def write(cls, index, mode=None):
        if mode is None:
            mode = cls.NORMAL
        if type(index) is not int:
            raise ValueError('index should be int')
        if mode not in cls.MODE:
            raise ValueError('"{}" is not supported'.format(mode))
        return super().write(stat, mode)


class SendSMSMessageCommand(NextLineArgCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CMGS"

    @classmethod
    def write(cls, *args, text=None, pdu=None):
        assert (text is None) ^ (pdu is None), "only one of 'text', 'pdu' should be provided"
        next_line_arg = None
        if text is not None:
            assert 1 <= len(args) <= 2, "for text mode the args are: <da>[, <toda>]"
            next_line_arg = text
        else:
            assert len(args) == 1, "for pdu mode the args are: <length>"
            next_line_arg = pdu

        return super().write(*args, next_line_arg=next_line_arg)


class WriteSMSMessageToMemoryCommand(NextLineArgCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE, ExtendedCommand.EXECUTE]
    BASE_CMD = "+CMGW"

    class _Mode:
        pass

    class _PduMode(_Mode):
        UNREAD = 0
        READ = 1
        UNSENT = 2
        SENT = 3

        STAT = [UNREAD, READ, UNSENT, SENT]

    class _TextMode(_Mode):
        UNSENT = "STO UNSENT"
        SENT = "STO SENT"

        STAT = [UNSENT, SENT]

    PDU_MODE = _PduMode()
    TEXT_MODE = _TextMode()

    @classmethod
    def write(cls, *args, text=None, pdu=None):
        assert (text is None) ^ (pdu is None), "only one of 'text', 'pdu' should be provided"
        next_line_arg = None
        if text is not None:
            assert 1 <= len(args) <= 3, "for text mode the args are: <oa/da>[, <tooa/toda>][, <stat>]"
            if len(args) > 2:
                stat = args[2]
                if stat not in cls.TEXT_MODE.STAT:
                    raise ValueError('"{}" is not supported'.format(stat))
            next_line_arg = text
        else:
            assert 1 <= len(args) <= 2, "for pdu mode the args are: <length>[, <stat>]"
            if len(args) > 1:
                stat = args[1]
                if stat not in cls.PDU_MODE.STAT:
                    raise ValueError('"{}" is not supported'.format(stat))
            next_line_arg = pdu

        return super().write(*args, next_line_arg=next_line_arg)


class SendSMSMessageFromStorageCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CMSS"
