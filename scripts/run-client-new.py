import lorem
import sys  # noqa

from bos_consensus.common import Message
from bos_consensus.network import Endpoint
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    logger,
)

from client.client import send_message_new

parser = ArgumentParserShowDefaults()

log = None
logger.set_argparse(parser)

parser.add_argument(
    'endpoints',
    nargs='+',
    help='endpoints, you want to send the message to',
    type=str,
)

parser.add_argument(
    'message',
    nargs='?',
    default=lorem.sentence().split()[0],
    help='Messages you want to send to the server',
    type=str,
)

if __name__ == '__main__':
    options = parser.parse_args()
    logger.from_argparse(logger, options)
    log = logger.get_logger(__name__)

    log.debug('options: %s', options)

    message_text = options.message
    endpoints = list()
    for n, i in enumerate(options.endpoints):
        try:
            endpoints.append(Endpoint.from_uri(i))
        except AssertionError as e:
            if n < len(options.endpoints) - 1:
                parser.error('invalid endpoint: %s' % i)

                sys.exit(1)

            message_text = i

    message = Message.new(message_text)

    log.info('trying to send message: %s' % message)
    message = send_message_new(message, *endpoints)
    log.info('sent message: %s', message.serialize(to_string=False))

    sys.exit(0)
