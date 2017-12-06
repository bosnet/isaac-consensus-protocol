import logging


log = logging.getLogger(__name__)


def not_found_handler(server, parsed):
    if parsed.path[1:] == '':
        return handle_ping(server, parsed)

    message = '"%s" not found' % parsed.path
    server.response(404, message)

    return


def handle_ping(server, parsed):
    if server.command not in ('POST',):
        server.response(405, None)
        return

    # length = int(server.headers['Content-Length'])
    # post_data = server.rfile.read(length).decode('utf-8')

    # d = json.loads(post_data)
    # host, _ = server.request.getpeername()
    # endpoint = 'http://%s:%s' % (host, d['port'])

    host, port = server.request.getsockname()
    info = dict(
        id=server.id,
        endpoint='http://%s:%s' % (host, port)
    )
    server.json_response(200, info)

    return


HTTP_HANDLERS = dict(
    ping=handle_ping,
    # ballot = handle_ballot
)
