import collections
import json
import logging
import time
import urllib

import colorlog
import requests

from bos_consensus.consensus import get_consensus_module
from bos_consensus.common.message import Message


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


MessageInfo = collections.namedtuple(
    'MessageInfo',
    ('ip', 'port', 'message'),
)


def send_message(message_info):
    assert isinstance(message_info, MessageInfo)
    log.debug('loaded message: %s', message_info)

    endpoint = 'http://%s:%s' % (message_info.ip, message_info.port)
    try:
        message = Message.new(message_info.message)
        response = requests.post(
            urllib.parse.urljoin(endpoint, '/send_message'),
            data=message.serialize(to_string=True),
        )
        response.raise_for_status()
        log.debug('message sent!')
    except requests.exceptions.ConnectionError:
        log.warn("ConnectionError occurred during client send message to '%s'!" % endpoint)
    except requests.exceptions.HTTPError:
        log.warn("HTTPError occurred during client send message to '%s'!" % endpoint)
