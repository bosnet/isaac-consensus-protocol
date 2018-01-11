import collections
import json
import logging
import time
import urllib

import colorlog
import requests

from bos_consensus.consensus import get_consensus_module


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

    consensus_module = get_consensus_module('simple_fba')

    url = 'http://%s:%s' % (message_info.ip, message_info.port)
    try:
        while(True):
            get_node_response = requests.get(urllib.parse.urljoin(url, '/get_node'))
            get_node_response.raise_for_status()
            json_data = json.loads(get_node_response.text)
            status = consensus_module.StateKind[json_data['status']]
            if status == consensus_module.StateKind.ALLCONFIRM or status == consensus_module.StateKind.INIT:
                json_data = json.dumps({'message': message_info.message})
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
