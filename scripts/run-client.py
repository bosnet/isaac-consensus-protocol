import lorem
import sys

from bos_consensus.util import (
    ArgumentParserShowDefaults,
    get_uuid,
    logger,
)

from client.client import (
    MessageInfo,
    send_message
)

parser = ArgumentParserShowDefaults()

log = None
logger.set_argparse(parser)

parser.add_argument(
    '-id',
    '--id',
    default=get_uuid(),
    help='Message id',
    type=str,
)
parser.add_argument(
    '-m',
    '--message',
    default=lorem.sentence().split()[0],
    help='Messages you want to send to the server',
    type=str,
)
parser.add_argument(
    '-i',
    '--ip',
    default='localhost',
    help='Server IP you want to send the message to',
    type=str,
)
parser.add_argument(
    '-p',
    '--port',
    default=5001,
    help='Server port you want to send the message to',
    type=int,
)


if __name__ == '__main__':
    options = parser.parse_args()
    logger.from_argparse(logger, options)
    log = logger.get_logger(__name__)

    log.debug('options: %s', options)

    log.info('Sending Message: %s' % options.message)

    message_info = MessageInfo(options.id, options.ip, options.port, options.message)

    message = send_message(message_info)
    if message is None:
        sys.exit(1)

    log.info('sent message: %s', message.serialize(to_string=False))
