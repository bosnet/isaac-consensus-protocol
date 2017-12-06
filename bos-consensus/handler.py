import logging


log = logging.getLogger(__name__)


def not_found_handler(handler, parsed):
    if parsed.path[1:] == '':
        return handle_ping(handler, parsed)

    message = '"%s" not found' % parsed.path
    handler.response(404, message)

    return


def handle_ping(handler, parsed):
    if handler.command not in ('POST',):
        handler.response(405, None)
        return

    handler.json_response(200, handler.server.nd.to_dict())

    return


HTTP_HANDLERS = dict(
    ping=handle_ping,
)
