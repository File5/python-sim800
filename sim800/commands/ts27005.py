from sim800.commands.command import Command, NoResponseCommand, ExtendedCommand, NextLineArgCommand
from sim800.results import Result


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


class NewSMSMessageIndicationCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CNMI"

    BUFFER = 0
    DISCARD_RESERVED = 1  # discard new message indications when TA-TE is reserved (serial is used for data)
    BUFFER_RESERVED = 2  # buffer new message indications when TA-TE is reserved (send when becomes free)
    BREAK_RESERVED = 3  # send BREAK when TA-TE is reserved

    MODE = [BUFFER, DISCARD_RESERVED, BUFFER_RESERVED, BREAK_RESERVED]

    NO_INDICATIONS = 0
    MEMORY_INDICATION = 1
    CLASS2_MEMORY_INDICATION_OTHER_REDIRECT = 2
    CLASS3_REDIRECT_OTHER_MEMORY_INDICATION = 3

    MT = [NO_INDICATIONS, MEMORY_INDICATION, CLASS2_MEMORY_INDICATION_OTHER_REDIRECT, CLASS3_REDIRECT_OTHER_MEMORY_INDICATION]

    CBM_NO_INDICATIONS = 0
    CBM_REDIRECT = 2

    BM = [CBM_NO_INDICATIONS, CBM_REDIRECT]

    REPORT_NO_INDICATIONS = 0
    REPORT_REDIRECT = 1

    DS = [REPORT_NO_INDICATIONS, REPORT_REDIRECT]

    # when MODE in {1, 2, 3} is entered
    BUFFER_FLUSHED = 0
    BUFFER_CLEARED = 1

    BFR = [BUFFER_FLUSHED, BUFFER_CLEARED]


class PreferredSMSMessageStorageCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CPMS"

    SIM = "SM"
    MODEM = "ME"
    SIM_PREFERRED = "SM_P"
    MODEM_PREFERRED = "ME_P"
    SIM_PREFERRED_OR_MODEM = "MT"

    MEM = [SIM, MODEM, SIM_PREFERRED, MODEM_PREFERRED, SIM_PREFERRED_OR_MODEM]
    # <mem1>; <mem2>; <mem3> -- read,delete; send,write; received


class SMSServiceCenterAddressCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+CSCA"

