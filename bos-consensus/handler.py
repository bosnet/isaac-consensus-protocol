import logging


log = logging.getLogger(__name__)


def not_found_handler(handler, parsed):
    if parsed.path[1:] == '':
        return handle_ping(handler, parsed)

    message = '"%s" not found' % parsed.path
    handler.response(404, message)

    return


def handle_ping(handler, parsed):
    if handler.command not in ('GET',):
        handler.response(405, None)
        return

    handler.json_response(200, handler.server.nd.to_dict())

    return


def handle_get_node(handler, parsed):
    if handler.command not in ('GET',):
        handler.response(405, None)
        return

    return handler.json_response(200, handler.server.nd.to_dict())


def handle_send_ballot(handler, parsed):
    if handler.command not in ('POST',):
        handler.response(405, None)
        return

    return handler.json_response(200, handler.server.nd.to_dict())


HTTP_HANDLERS = dict(
    ping=handle_ping,
    get_node=handle_get_node,
    send_ballot=handle_send_ballot,
)
