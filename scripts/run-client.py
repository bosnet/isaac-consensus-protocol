import argparse
from essential_generators import DocumentGenerator

from bos_consensus.util import (
    logger,
)

from client.client import (
    MessageInfo,
    send_message
)

parser = argparse.ArgumentParser()

log = None
logger.set_argparse(parser)

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
    options = parser.parse_args()
    logger.from_argparse(logger, options)

    log = logger.get_logger(__name__)

    log.debug('options: %s', options)

    log.info('Sending Message: %s' % options.message)

    message_info = MessageInfo(options.ip, options.port, options.message)

    send_message(message_info)
