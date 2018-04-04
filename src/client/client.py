import collections
from multiprocessing import Process, Queue
import urllib

import requests

from bos_consensus.common import Message
from bos_consensus.util import (
    get_uuid,
    logger,
)


MessageInfo = collections.namedtuple(
    'MessageInfo',
    ('id', 'ip', 'port', 'message'),
)


def send_message(message_info):
    assert isinstance(message_info, MessageInfo)

    log = logger.get_logger('client')
    log.debug('loaded message: %s', message_info)

    endpoint = 'http://%s:%s' % (message_info.ip, message_info.port)
    try:
        message = Message(message_info.id, message_info.message)
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


def _send_message_multiple_one(queue, message, endpoint):
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


def _send_message_multiple(queue, message, endpoint, message_id=None):
    create_new_message = message is None
    messages = [message] if message is not None else list()

    number_of_messages = int(endpoint.get('m', 1))
    q = Queue(maxsize=number_of_messages)
    for i in range(number_of_messages):
        if create_new_message:
            new_message = Message.new()
            if message_id:
                new_message.message_id = message_id

            messages.append(new_message)

        p = Process(target=_send_message_multiple_one, args=(q, messages[-1], endpoint))
        p.start()

    while not q.full():
        pass

    queue.put(messages)

    return


def send_message_multiple(message, *endpoints, same_message_id=False):
    message_id = None
    if same_message_id is True:
        message_id = get_uuid()

    if message_id is not None and message is not None:
        message.message_id = message_id

    q = Queue(maxsize=len(endpoints))
    for endpoint in endpoints:
        p = Process(
            target=_send_message_multiple,
            args=(q, message, endpoint),
            kwargs=dict(message_id=message_id),
        )
        p.start()

    while not q.full():
        pass

    messages = list()
    for i in endpoints:
        messages.extend(map(lambda x: (x, i), q.get()))

    return messages
