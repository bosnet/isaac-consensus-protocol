from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import logging

import handler
from node import Node


log = logging.getLogger(__name__)


class BOSNetHTTPServer(HTTPServer):
    nd = None

    def __init__(self, nd, *a, **kw):
        assert isinstance(nd, Node)

        super(BOSNetHTTPServer, self).__init__(*a, **kw)

        self.nd = nd

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self)

        return

    @property
    def endpoint(self):
        return self.nd.endpoint


class BOSNetHTTPServerRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super(BOSNetHTTPServerRequestHandler, self).__init__(*a, **kw)

    def do_GET(self):
        log.debug('> start request: %s', self.path)
        parsed = urlparse(self.path)
        func = handler.HTTP_HANDLERS.get(parsed.path[1:].split('/')[0], handler.not_found_handler)
        r = func(self, parsed)

        log.debug('< finished request: %s', self.path)
        return r

    do_POST = do_GET

    def response(self, status_code, message, **headers):
        self.send_response(status_code)
        for k, v in headers.items():
            self.send_header(k, v)

        self.end_headers()

        if message is not None:
            self.wfile.write(bytes(message + ('\n' if message[-1] != '\n' else ''), "utf8"))

        return

    def json_response(self, status_code, message, **headers):
        if type(message) not in (str,):
            message = json.dumps(message)

        headers['Content-Type'] = 'application/json'

        return self.response(status_code, message, **headers)
