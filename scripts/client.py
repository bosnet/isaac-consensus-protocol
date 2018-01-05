import argparse
import collections
import json
import logging
import requests
import time
import urllib
import colorlog

from bos_consensus.consensus import get_consensus_module
simple_fba_module = get_consensus_module('simple_fba')
StateKind = simple_fba_module.StateKind

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
parser.add_argument('-debug', action='store_true', help='Log level set to debug')
parser.add_argument('-info', action='store_true', help='Log level set to info')
parser.add_argument(
    '-m',
    '--message',
    required=True,
    help='Messages you want to send to the server.',
    type=str,
)
parser.add_argument(
    '-i',
    '--ip',
    required=True,
    help='Server IP you want to send the message to.',
    type=str,
)
parser.add_argument(
    '-p',
    '--port',
    required=True,
    help='Server port you want to send the message to.',
    type=int,
)

if __name__ == '__main__':
    log_level = logging.ERROR

    options = parser.parse_args()

    if options.debug:
        log_level = logging.DEBUG

    if options.info:
        log_level = logging.INFO

    log.root.setLevel(log_level)

    log.debug('options: %s', options)

    config = collections.namedtuple(
        'Config',
        ('ip', 'port', 'message'),
    )('localhost', 5001, 'message')

    log.info('Sending Message: %s' % options.message)

    config = config._replace(ip=options.ip)
    config = config._replace(port=options.port)
    config = config._replace(message=options.message)
    log.debug('loaded conf: %s', config)

    url = 'http://%s:%s' % (config.ip, config.port)
    try:
        while(True):
            get_node_response = requests.get(urllib.parse.urljoin(url, '/get_node'))
            get_node_response.raise_for_status()
            json_data = json.loads(get_node_response.text)
            status = StateKind[json_data['status']]
            if status == StateKind.ALLCONFIRM or status == StateKind.INIT:
                json_data = json.dumps({'message': config.message})
                response = requests.post(urllib.parse.urljoin(url, '/send_message'), data=json_data)
                response.raise_for_status()
                log.debug('message sent!')
                break
            else:
                time.sleep(1)
    except requests.exceptions.ConnectionError:
        log.warn("ConnectionError occurred during client send message to '%s'!" % url)
    except requests.exceptions.HTTPError:
        log.warn("HTTPError occurred during client send message to '%s'!" % url)
