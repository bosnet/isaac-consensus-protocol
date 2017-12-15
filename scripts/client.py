import argparse
import collections
import logging
import urllib
import colorlog
import requests


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
parser.add_argument('-m', '--message', required=True, help='Messages you want to send to the server.', type=str)
parser.add_argument('-i', '--ip', required=True, help='Server IP you want to send the message to.', type=str)
parser.add_argument('-p', '--port', required=True, help='Server port you want to send the message to.', type=int)

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

    log.info('Sending Message: %s' % options.message)

    config = config._replace(ip=options.ip)
    config = config._replace(port=options.port)
    config = config._replace(message=options.message)
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
