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


conf = configparser.ConfigParser()
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


if __name__ == '__main__':
    options = collections.namedtuple(
        'Options',
        ('id', 'port', 'validators'),
    )(uuid.uuid1().hex, 8001, [])

    if len(sys.argv) != 2:
        error_message = 'usage: %s <config ini>' % (sys.argv[0],)
        print(error_message)
        log.error(error_message)
        exit(2)

    input_ini_path = sys.argv[1].strip('"\'')
    if not pathlib.Path(input_ini_path).is_file():
        error_message = 'File "' + input_ini_path + '" not exists!'
        print(error_message)
        log.error(error_message)
        exit(2)

    log.info('Ini file path: "' + input_ini_path + '"')
    log.root.setLevel(logging.DEBUG)
    conf.read(input_ini_path)
    options = options._replace(id=conf['NODE']['ID'])
    log.debug('Node ID: %s' % options.id)

    options = options._replace(port=int(conf['NODE']['PORT']))
    log.debug('Node PORT: %s' % options.port)

    validator_list = []
    for i in filter(lambda x: len(x.strip()) > 0, conf['NODE']['VALIDATOR_LIST'].split(',')):
        validator_list.append(i.strip())

    options = options._replace(validators=validator_list)
    log.debug('Validators: %s' % options.validators)

    node_address = ('0.0.0.0', options.port)
    httpd = BOSNetHTTPServer(
        options.id,
        options.validators,
        node_address,
        BOSNetHTTPServerRequestHandler,
    )

    httpd.serve_forever()
