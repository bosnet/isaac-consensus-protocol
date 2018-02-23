import collections
from multiprocessing import Process, Queue
import urllib

import requests

from bos_consensus.common import Message
from bos_consensus.util import logger


MessageInfo = collections.namedtuple(
    'MessageInfo',
    ('ip', 'port', 'message'),
)


def send_message(message_info):
    assert isinstance(message_info, MessageInfo)

    log = logger.get_logger('client')
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
    except Exception as e:
        log.error("ConnectionError occurred during client send message to '%s'!" % endpoint)

        return

    return message


def _send_message_new(queue, message, endpoint):
    log = logger.get_logger('client')
    try:
        response = requests.post(
            endpoint.join('/send_message'),
            data=message.serialize(to_string=True),
        )
        response.raise_for_status()
        log.debug('sent message, %s to %s', message, endpoint)
    except Exception as e:
        log.error("failed to send message, %s to %s", message, endpoint)

        queue.put(False)

        return

    queue.put(True)

    return


def send_message_new(message, *endpoints):
    q = Queue(maxsize=len(endpoints))
    for endpoint in endpoints:
        p = Process(target=_send_message_new, args=(q, message, endpoint))
        p.start()

    while not q.full():
        pass

    return message
