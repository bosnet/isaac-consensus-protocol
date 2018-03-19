import argparse
from calendar import timegm
from collections import namedtuple
from contextlib import closing
import datetime
import importlib
import logging
import os
from pythonjsonlogger import jsonlogger
import socket
import sys
from termcolor import colored
import time
import uuid


try:
    _, TERMINAL_COLUMNS = os.popen('stty size', 'r').read().split()
except ValueError:
    TERMINAL_COLUMNS = 0
else:
    TERMINAL_COLUMNS = int(TERMINAL_COLUMNS)

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


class ArgumentParserShowDefaults(argparse.ArgumentParser):
    def __init__(self, *a, **kw):
        super(ArgumentParserShowDefaults, self).__init__(*a, **kw)

        self.formatter_class = argparse.ArgumentDefaultsHelpFormatter


class PartialLog:
    extras = None

    def __init__(self, logger, **extras):
        self.logger = logger
        self.extras = extras

    def set_level(self, level):
        return self.logger.setLevel(level)

    def getLevel(self):
        return self.logger.level

    def _write(self, n, msg, *a, **kw):
        msg = '%s - %s' % (msg, self.extras)
        return getattr(self.logger, n)(msg, *a, **kw)

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
        self.json_formatter = JsonFormatter(json_indent=2 if self.in_terminal else None)
        self.json_formatter_output = JsonFormatter()
        self.stream_metric = None

    def emit(self, record):
        formatted = None
        formatted_output = None
        if record.levelno == LOG_LEVEL_METRIC:
            record.msg['created'] = record.created
            formatted = self.json_formatter.format(record)
            formatted_output = self.json_formatter_output.format(record)
            level_name = 'METR'
        else:
            formatted = self.format(record)
            level_name = record.levelname[:4]

        prefix = ''
        if self.in_terminal:
            prefix = '● '

        line = ''
        if self.in_terminal and self.logger.is_show_line:
            line = self.terminator + '%s' % ('─' * int(TERMINAL_COLUMNS))

        msg = '%s%0.8f - %s - %-4s - %s%s' % (prefix, record.created, record.name, level_name, formatted, line)

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

            self.stream_metric.write(formatted_output)
            self.stream_metric.write(self.terminator)
            self.stream_metric.flush()

        return


class Logger:
    log_format = '%%(msecs)f - %%(name)s - %%(message)s'
    level = None
    levels = None
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
        parser.add_argument(
            '-log-level',
            default='debug',
            type=str,
            help='set log level',
            choices=AVAILABLE_LOGGING_LEVELS,
        )
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
        self.levels = dict()
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

    def set_level(self, level, name=None):
        if name is not None:
            self.levels[name] = level

            return

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
        logger.setLevel(self.levels.get(name, self.level))

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


def get_module(name, package=None):
    try:
        return importlib.import_module(name, package=package)
    except ModuleNotFoundError as e:
        log.error(e)
        return None


def convert_dict_to_namedtuple(d):
    if type(d) not in (dict,):
        return d

    n = dict()
    for k, v in d.items():
        if type(v) in (dict,):
            n[k] = convert_dict_to_namedtuple(v)
        elif type(v) in (list, tuple):
            n[k] = list(map(convert_dict_to_namedtuple, v))
        else:
            n[k] = v

    return namedtuple('BOSDict', n.keys())(**n)


def convert_namedtuple_to_dict(v):
    if not hasattr(v, '_asdict'):
        return v

    n = dict()
    for k, v in v._asdict().items():
        if v.__class__.__name__ in ('BOSDict',):
            n[k] = convert_namedtuple_to_dict(v)
        else:
            n[k] = v

    return n


def get_free_port(defined=None):
    if defined is None:
        defined = list()

    port = None
    while port is None or port in defined:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            port = s.getsockname()[1]

    return port


def utcnow():
    return datetime.datetime.now().utcnow()


def datetime_to_timestamp(d):
    return timegm(d.utctimetuple())


def convert_json_config(config):
    validator_dict = {}
    faulty_dict = {}

    if 'groups' in config:
        groups = config['groups']
        validator_dict = groupset_to_node_validatorset(groups)
        del config['groups']

    if 'unary_link' in config:
        unary = config['unary_link']
        validator_dict = add_unary_validate(unary, validator_dict)
        del config['unary_link']

    if 'binary_link' in config:
        binary = config['binary_link']
        validator_dict = add_binary_validate(binary, validator_dict)
        del config['binary_link']

    if 'nodes' in config:
        nodes = config['nodes']
        config['faulties'] = dict()
        for node in nodes:
            if 'threshold' in nodes[node]:
                validator_dict[node]['quorum']['threshold'] = nodes[node]['threshold']

            if 'faulty_kind' in nodes[node]:
                case_dict = {}
                faulty_dict[node] = []
                case_dict.setdefault('case', dict())['kind'] = nodes[node]['faulty_kind']
                faulty_dict[node].append(case_dict)

                if 'faulty_percent' in nodes[node]:
                    for node_case in faulty_dict[node]:
                        node_case['case']['frequency'] = nodes[node]['faulty_percent']

                    if isinstance(nodes[node]['faulty_percent'], dict):
                        for node_case in faulty_dict[node]:
                            node_case['case']['frequency']['per_consensus'] = nodes[node]['faulty_percent']['per_consensus']  # noqa

                if 'duration' in nodes[node]:
                    for node_case in faulty_dict[node]:
                        node_case['case']['duration'] = nodes[node]['duration']

                if 'target_nodes' in nodes[node]:
                    for node_case in faulty_dict[node]:
                        node_case['case']['target_nodes'] = nodes[node]['target_nodes']

        del config['nodes']

    config['nodes'] = validator_dict
    config['faulties'] = faulty_dict

    return config


def groupset_to_node_validatorset(group_dict):
    node_list = {}
    for group_name in group_dict:
        for from_node in group_dict[group_name]:
            if from_node not in node_list:
                node_list.setdefault(from_node, dict()).setdefault('quorum', dict()).setdefault('validators', list())
            for to_node in group_dict[group_name]:
                if (to_node not in node_list[from_node]) and (to_node != from_node):
                    node_list[from_node]['quorum']['validators'].append(to_node)

    return node_list


def add_unary_validate(unaryLink_list, validatorList):
    node_list = validatorList
    for nodes in unaryLink_list:
        node_list = add_nodes(nodes[0], nodes[1], node_list)

    return node_list


def add_binary_validate(binaryLink_list, validatorList):
    node_list = validatorList
    for nodes in binaryLink_list:
        node_list = add_nodes(nodes[0], nodes[1], node_list)
        node_list = add_nodes(nodes[1], nodes[0], node_list)

    return node_list


def add_nodes(from_nodes, to_nodes, validatorList):
    node_list = validatorList

    if isinstance(from_nodes, (list, tuple,)):
        for from_node in from_nodes:
            if from_node not in node_list:
                node_list.setdefault(from_node, dict()).setdefault('quorum', dict()).setdefault('validators', list())

            if isinstance(to_nodes, (list,)):
                for to_node in to_nodes:
                    if (to_node not in node_list[from_node]) and (to_node != from_node):
                        node_list[from_node]['quorum']['validators'].append(to_node)

            else:
                node_list[from_node].append(to_nodes)
    else:
        if from_nodes not in node_list:
            node_list.setdefault('from_nodes', dict()).setdefault('quorum', dict()).setdefault('validators', list())

        if isinstance(to_nodes, (list, tuple,)):
            for to_node in to_nodes:
                if to_node not in node_list[from_nodes] and to_node != from_nodes:
                    node_list[from_nodes]['quorum']['validators'].append(to_node)

        else:
            node_list[from_nodes]['quorum']['validators'].append(to_nodes)

    return node_list


class Printer:
    out = None

    def __init__(self, out):
        self.out = out

    def print(self, *a, **kw):
        end = kw.get('end', '\n')

        t = ' '.join(a)
        if sys.stdout.isatty() and 'color' in kw and kw['color'] is not None:
            t = colored(t, kw['color'], attrs=kw.get('attrs'))

        self.out.write(t)
        self.out.write(end)
        self.out.flush()

        return

    def colored(self, *a, **kw):
        if not sys.stdout.isatty():
            return a[0]

        return colored(*a, **kw)

    def line(self, c=None):
        if c is None:
            c = '-'

        self.print(c * (TERMINAL_COLUMNS - 1), color='grey', attrs=('bold',))

        return

    def head(self, s):
        self.print('# %s' % s, color='cyan')

    def format(self, *a, **kw):
        fmt = kw.get('fmt')
        if fmt is not None:
            t = fmt % tuple(a)
        else:
            t = ' | '.join(a)

        if kw.get('print', False):
            return self.print(t, **kw)

        return t
