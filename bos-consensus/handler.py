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

    # length = int(handler.headers['Content-Length'])
    # post_data = handler.rfile.read(length).decode('utf-8')

    # d = json.loads(post_data)
    # host, _ = handler.request.getpeername()
    # endpoint = 'http://%s:%s' % (host, d['port'])

    info = dict(
        node_id=handler.server.node_id,
        validators=handler.server.validators,
        endpoint=handler.server.endpoint,
    )
    handler.json_response(200, info)

    return


HTTP_HANDLERS = dict(
    ping=handle_ping,
    # ballot = handle_ballot
)
