import json
import logging
import random
import time
from urllib.parse import (urlparse, parse_qs)

from .ballot import Ballot
from .statekind import StateKind

log = logging.getLogger(__name__)


def not_found_handler(handler, parsed):
    if parsed.path[1:] == '':
        return handle_ping(handler, parsed)

    message = '"%s" not found' % parsed.path
    handler.response(404, message)

    return


def handle_status(handler, parsed):
    if handler.command not in ('GET',):
        handler.response(405, None)
        return

    info = json.dumps({'Version':handler.server.version, 'Node':handler.server.node.to_dict()}, indent=True)
    handler.response(200, info)

    return


def handle_ping(handler, parsed):
    if handler.command not in ('GET',):
        handler.response(405, None)
        return

    handler.response(200, None)

    return


def handle_get_node(handler, parsed):
    if handler.command not in ('GET',):
        handler.response(405, None)
        return

    return handler.json_response(200, handler.server.node.to_dict())


def handle_send_message(handler, parsed):
    if handler.command not in ('POST',):
        handler.response(405, None)
        return

    time.sleep(random.random())

    json_data = parse_qs(parsed.query)
    message = json_data['message']
    handler.server.node_sequence_executor('receive_message_from_client', message[0])

    return handler.response(200, None)


def handle_send_ballot(handler, parsed):
    if handler.command not in ('POST',):
        handler.response(405, None)
        return

    json_data = parse_qs(parsed.query)
    ballot_num = json_data['ballot_num'][0]
    node_id = json_data['node_id'][0]
    message = json_data['message'][0]
    node_state_name = json_data['node_state_kind'][0]
    state_kind = StateKind[node_state_name]

    ballot = Ballot(ballot_num, node_id, message, state_kind)
    handler.server.node_sequence_executor('receive_ballot', ballot)

    return handler.response(200, None)


HTTP_HANDLERS = dict(
    status=handle_status,
    ping=handle_ping,
    get_node=handle_get_node,
    send_message=handle_send_message,
    send_ballot=handle_send_ballot,
)
