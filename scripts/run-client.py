import argparse
import colorlog
import logging
from essential_generators import DocumentGenerator

from client.client import (
    MessageInfo,
    send_message
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
parser.add_argument('-debug', action='store_true', help='Log level set to debug')
parser.add_argument('-info', action='store_true', help='Log level set to info')

parser.add_argument(
    '-m',
    '--message',
    default=DocumentGenerator().sentence(),
    help='Messages you want to send to the server.',
    type=str,
)
parser.add_argument(
    '-i',
    '--ip',
    default='localhost',
    help='Server IP you want to send the message to.',
    type=str,
)
parser.add_argument(
    '-p',
    '--port',
    default=5001,
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

    log.info('Sending Message: %s' % options.message)

    message_info = MessageInfo(options.ip, options.port, options.message)

    send_message(message_info)
