from sim800.commands.command import Command, ExtendedCommand


class PowerOffCommand(Command):
    def __init__(self, normal=True):
        cmd_string = "+CPOWD="
        cmd_string += "1" if normal else "0"
        super().__init__(cmd_string, ['NORMAL POWER DOWN'])


class TimesRemainedToInputPINPUKCommand(Command):
    def __init__(self):
        super().__init__("+SPIC", ['+SPIC:'])


class DeleteAllSMSMessagesCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.WRITE]
    BASE_CMD = "+CMGDA"

    class _Mode:
        pass

    class _PduMode(_Mode):
        READ = 1
        UNREAD = 2
        SENT = 3
        UNSENT = 4
        RECEIVED = 5
        ALL = 6

        DEL_FLAG = [READ, UNREAD, SENT, UNSENT, RECEIVED, ALL]

    class _TextMode(_Mode):
        READ = "DEL READ"
        UNREAD = "DEL UNREAD"
        SENT = "DEL SENT"
        UNSENT = "DEL UNSENT"
        RECEIVED = "DEL INBOX"
        ALL = "DEL ALL"

        DEL_FLAG = [READ, UNREAD, SENT, UNSENT, RECEIVED, ALL]

    PDU_MODE = _PduMode()
    TEXT_MODE = _TextMode()

    @classmethod
    def write(cls, del_flag):
        if del_flag not in cls.TEXT_MODE.DEL_FLAG + cls.PDU_MODE.DEL_FLAG:
            raise ValueError('{} is not supported'.format(del_flag))
        return super().write(del_flag)


class DisplayProductIdentificationInfoCommand(Command):
    def __init__(self):
        super().__init__("+GSV", ['SIM', 'Revision:'])


class RejectIncomingCallCommand(ExtendedCommand):
    COMMANDS = [ExtendedCommand.TEST, ExtendedCommand.READ, ExtendedCommand.WRITE]
    BASE_CMD = "+GSMBUSY" 

    ALLOW = 0
    FORBID_ALL = 1
    FORBID_ALL_BUT_CSD = 2

    MODE = [ALLOW, FORBID_ALL, FORBID_ALL_BUT_CSD]

    @classmethod
    def write(cls, mode=None):
        if mode is None:
            mode = cls.ALLOW
        if mode not in cls.MODE:
            raise ValueError('{} is not supported'.format(mode))
        return super().write(mode)

