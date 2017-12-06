import argparse
import collections
import colorlog
import configparser
import logging
import pathlib
import sys
import uuid

from network import (
    BOSNetHTTPServer,
    BOSNetHTTPServerRequestHandler,
)


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

log_handler = colorlog.StreamHandler()
log_handler.setFormatter(
    colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
    ),
)

logging.root.handlers = [log_handler]

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-debug', action='store_true')
parser.add_argument('conf', help='ini config file')


if __name__ == '__main__':
    log_level = logging.ERROR
    if '-debug' in sys.argv[1:]:
        log_level = logging.DEBUG

    log.root.setLevel(log_level)

    options = parser.parse_args()
    log.debug('options: %s', options)

    config = collections.namedtuple(
        'Config',
        ('id', 'port', 'validators'),
    )(uuid.uuid1().hex, 8001, [])

    if not pathlib.Path(options.conf).exists():
        parser.error('conf file, `%s` does not exists.' % options.conf)

    if not pathlib.Path(options.conf).is_file():
        parser.error('conf file, `%s` is not valid file.' % options.conf)

    conf = configparser.ConfigParser()
    conf.read(options.conf)
    log.info('conf file, `%s` was loaded', options.conf)

    config = config._replace(id=conf['NODE']['ID'])
    config = config._replace(port=int(conf['NODE']['PORT']))
    log.debug('loaded conf: %s', config)

    validator_list = []
    for i in filter(lambda x: len(x.strip()) > 0, conf['NODE']['VALIDATOR_LIST'].split(',')):
        validator_list.append(i.strip())

    config = config._replace(validators=validator_list)
    log.debug('Validators: %s' % config.validators)

    node_address = ('0.0.0.0', config.port)
    httpd = BOSNetHTTPServer(
        config.id,
        config.validators,
        node_address,
        BOSNetHTTPServerRequestHandler,
    )

    httpd.serve_forever()
