import sys  # noqa

from bos_consensus.common import Message
from bos_consensus.network import Endpoint
from bos_consensus.util import (
    ArgumentParserShowDefaults,
    logger,
)

from client.client import send_message_multiple


parser = ArgumentParserShowDefaults()

log = None
logger.set_argparse(parser)

parser.add_argument(
    'endpoints',
    nargs='+',
    help='endpoints with the number of endpoints\'s messages want to send; ex) http://localhost:80?m=5 http://localhost:80?m=10',  # noqa
    type=str,
)

parser.add_argument(
    'message',
    nargs='?',
    help='Messages you want to send to the server',
    type=str,
)

if __name__ == '__main__':
    options = parser.parse_args()
    logger.from_argparse(logger, options)
    log = logger.get_logger(__name__)

    log.debug('options: %s', options)

    message = None
    endpoints = list()
    for n, i in enumerate(options.endpoints):
        try:
            endpoints.append(Endpoint.from_uri(i))
        except AssertionError as e:
            if n < len(options.endpoints) - 1:
                parser.error('invalid endpoint: %s' % i)

                sys.exit(1)

            message = Message.new(i)

    log.debug('trying to send message, %s to %s', message, endpoints)
    messages = send_message_multiple(message, *endpoints)
    for (message, endpoint) in messages:
        log.debug('sent message, %s to %s', message.serialize(to_string=False), endpoint)

    sys.exit(0)
