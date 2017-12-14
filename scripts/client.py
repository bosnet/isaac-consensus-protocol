import argparse
import collections
import colorlog
import configparser
import logging
import pathlib
import sys
import uuid
import requests
import urllib


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
parser.add_argument('-info', action='store_true')
parser.add_argument('conf', help='ini config file for client')


if __name__ == '__main__':
    log_level = logging.ERROR

    options = parser.parse_args()

    if options.debug == True:
        log_level = logging.DEBUG

    if options.info == True:
        log_level = logging.INFO

    log.root.setLevel(log_level)

    log.debug('options: %s', options)

    config = collections.namedtuple(
        'Config',
        ('ip', 'port', 'message'),
    )('localhost', 5001, 'message')

    if not pathlib.Path(options.conf).exists():
        parser.error('conf file, `%s` does not exists.' % options.conf)

    if not pathlib.Path(options.conf).is_file():
        parser.error('conf file, `%s` is not valid file.' % options.conf)

    conf = configparser.ConfigParser()
    conf.read(options.conf)
    log.info('conf file, `%s` was loaded', options.conf)

    config = config._replace(ip=conf['client']['ip'])
    config = config._replace(port=int(conf['client']['port']))
    config = config._replace(message=conf['client']['message'])
    log.debug('loaded conf: %s', config)

    url = 'http://%s:%s' % (config.ip, config.port)
    json_data = {'message': config.message}
    try:
        response = requests.post(urllib.parse.urljoin(url, '/send_message'), params=json_data)
        if response.status_code == 200:
            log.debug('message sent!')
        else:
            log.error('message sent error')
    except requests.exceptions.ConnectionError:
        log.info('Connection Refused!')
