import argparse
import logging
from pythonjsonlogger import jsonlogger
import os
import socket
import time
import uuid
import sys
from termcolor import colored


try:
    _, TERMINAL_COLUMNS = os.popen('stty size', 'r').read().split()
except ValueError:
    TERMINAL_COLUMNS = 0

AVAILABLE_LOGGING_LEVELS = tuple(map(
    lambda x: x.lower(),
    filter(lambda x: x not in ('NOTSET',), logging._nameToLevel.keys()),
))

LOG_LEVEL_METRIC = logging.CRITICAL + 10


def get_local_ipaddress():
    return socket.gethostbyname('localhost')


CLOCK_SEQ = int(time.time() * 1000000)


def get_uuid():
    return uuid.uuid1(clock_seq=CLOCK_SEQ).hex


class PartialLog:
    extras = None

    def __init__(self, logger, **extras):
        self.logger = logger
        self.extras = extras

    def set_level(self, level):
        return self.logger.setLevel(level)

    def getLevel(self):
        return self.logger.level

    def _write(self, n, *a, **kw):
        return getattr(self.logger, n)(*a, **kw)

    def debug(self, *a, **kw):
        return self._write('debug', *a, **kw)

    def info(self, *a, **kw):
        return self._write('info', *a, **kw)

    def warn(self, *a, **kw):
        return self._write('warn', *a, **kw)

    warning = warn

    def fatal(self, *a, **kw):
        return self._write('fatal', *a, **kw)

    def critical(self, *a, **kw):
        return self._write('critical', *a, **kw)

    def error(self, *a, **kw):
        return self._write('error', *a, **kw)

    def metric(self, **kw):
        kw['logger'] = self.logger.name
        kw.update(self.extras)

        return self.logger._log(LOG_LEVEL_METRIC, kw, None, None)


class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, *a, **kw):
        super(JsonFormatter, self).add_fields(log_record, *a, **kw)

        if 'message' in log_record and log_record['message'] is None:
            del log_record['message']

        return


class LogStreamHandler(logging.StreamHandler):
    logger = None
    stream_metric = None

    in_terminal = sys.stdout.isatty()

    def __init__(self, logger, *a, **kw):
        super(LogStreamHandler, self).__init__(*a, **kw)

        self.logger = logger
        self.json_formatter = JsonFormatter()
        self.stream_metric = None

    def emit(self, record):
        if self.in_terminal:
            _, columns = os.popen('stty size', 'r').read().split()

        if record.levelno == LOG_LEVEL_METRIC:
            record.msg['created'] = record.created
            formatted = self.json_formatter.format(record)
            level_name = 'METRI'
        else:
            formatted = self.format(record)
            level_name = record.levelname[:5]

        prefix = ''
        if self.in_terminal:
            prefix = '● '

        line = ''
        if self.in_terminal and self.logger.is_show_line:
            line = self.terminator + '%s' % ('─' * int(TERMINAL_COLUMNS))

        msg = '%s%0.8f - %-5s - %s%s' % (prefix, record.created, level_name, formatted, line)

        if self.in_terminal and self.logger.is_show_color:
            color = self.logger.colors.get(record.levelno)
            if color:
                msg = colored(msg, color)

        try:
            stream = self.stream
            stream.write(msg)
            stream.write(self.terminator)

            self.flush()
        except Exception:
            self.handleError(record)

        if record.levelno == LOG_LEVEL_METRIC and self.logger.output_metric is not None:
            if self.stream_metric is None:
                self.stream_metric = open(self.logger.output_metric, 'a')

            self.stream_metric.write(formatted)
            self.stream_metric.write(self.terminator)
            self.stream_metric.flush()

        return


class Logger:
    log_format = '%%(msecs)f - %%(name)s - %%(message)s'
    level = None
    output = None
    output_metric = None
    is_show_line = None
    is_show_color = None

    colors = {
        logging.INFO: 'green',
        logging.WARN: 'yellow',
        logging.FATAL: 'red',
        logging.CRITICAL: 'magenta',
        logging.ERROR: 'red',
        LOG_LEVEL_METRIC: 'blue',
    }

    @classmethod
    def set_argparse(cls, parser):
        parser.add_argument('-verbose', action='store_true', default=False, help='verbose log')
        parser.add_argument('-log-level', type=str, help='set log level', choices=AVAILABLE_LOGGING_LEVELS)
        parser.add_argument('-log-output', type=str, help='set log output file')
        parser.add_argument('-log-output-metric', type=str, help='set metric output file')
        parser.add_argument('-log-show-line', action='store_true', default=False, help='show seperate lines in log')
        parser.add_argument(
            '-log-no-color',
            action='store_true',
            default=False,
            help='disable colorized log message by level',
        )

        return parser

    @classmethod
    def from_argparse(cls, logger, options):
        assert isinstance(options, argparse.Namespace)

        if options.verbose:
            logger.set_level(logging.DEBUG)
        elif options.log_level:
            logger.set_level(logging.getLevelName(options.log_level.upper()))
        else:
            logger.set_level(logging.ERROR)

        if options.log_output:
            logger.set_output(options.log_output)

        if options.log_output_metric:
            logger.set_output_metric(options.log_output_metric)

        if options.log_show_line:
            logger.show_line(options.log_show_line)

        if options.log_no_color:
            logger.show_color(not options.log_no_color)

        return logger

    def __init__(self):
        self.level = logging.ERROR
        self.output = None
        self.output_metric = None
        self.is_show_line = False
        self.is_show_color = True

        logging.basicConfig(format=self.log_format)

        log_handler = LogStreamHandler(self)
        logging.root.handlers = [log_handler]

        return

    @property
    def info(self):
        return dict(
            level=logging.getLevelName(self.level),
            output=self.output,
            output_metric=self.output_metric,
            show_line=self.is_show_line,
        )

    def set_level(self, level):
        self.level = level

        return

    def set_output(self, f):
        self.output = f
        handler = logging.FileHandler(self.output)
        logging.root.addHandler(handler)

        return

    def show_line(self, s=None):
        assert type(s) in (bool,)

        self.is_show_line = s

        return

    def set_output_metric(self, f):
        self.output_metric = f

        return

    def show_color(self, s):
        assert type(s) in (bool,)

        self.is_show_color = s

        return

    def get_logger(self, name, **extras):
        logger = logging.getLogger(name)
        logger.setLevel(self.level)

        return PartialLog(logger, **extras)


class LoggingMixin:
    log = None

    def __init__(self):
        self.log = None

    def set_logging(self, logger_name, **extras):
        self.log = logger.get_logger(logger_name, **extras)

        return


logger = Logger()
log = logger.get_logger('util')
