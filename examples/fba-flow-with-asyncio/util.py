import colorlog
import enum
import logging
import sys


class Log:
    main = logging.getLogger('MAIN')
    transport = logging.getLogger('TRANSPORT')
    server = logging.getLogger('SERVER')
    consensus = logging.getLogger('CONSENSUS')
    ballot = logging.getLogger('BALLOT')
    storage = logging.getLogger('STORAGE')

    log_format = '%(msecs)f - %(name)s - %(message)s'
    if sys.stdout.isatty():
        colorlog_format = '%(log_color)s' + log_format
    else:
        colorlog_format = log_format

    def __init__(self):
        logging.basicConfig(
            format='%(msecs)f - %(name)s - %(message)s',
        )

        if sys.stdout.isatty():
            log_handler = colorlog.StreamHandler()
            log_handler.setFormatter(
                colorlog.ColoredFormatter(
                    self.colorlog_format,
                    reset=True,
                    log_colors={
                        'DEBUG': 'white',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    },
                ),
            )
            logging.root.handlers = [log_handler]

    def set_level(self, level):
        self.main.setLevel(level)
        self.server.setLevel(level)
        self.server.setLevel(level)
        self.consensus.setLevel(level)
        self.ballot.setLevel(level)
        self.storage.setLevel(level)

        return


log = Log()


class BaseEnum(enum.Enum):
    @classmethod
    def from_value(cls, value):
        for i in cls:
            if i.value == value:
                return i

        return None

    @classmethod
    def from_name(cls, name):
        return getattr(cls, name)
