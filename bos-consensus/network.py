from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import logging

import handler
from node import Node
import threading
import requests
import urllib
import urlparse
import time


log = logging.getLogger(__name__)


class Ping(threading.Thread):
    def __init__(self, node):
        super(Ping, self).__init__()
        self.node = node

    def run(self):
        url = 'http://%s'
        while True:
            time.sleep(1)

            if len(self.node.validators) == len(self.node.validator_addrs):
                self.node.init_node()
                break

            for addr in self.node.validator_addrs:
                res_ping = requests.get(
                    urllib.parse.urljoin(url % addr, '/ping')
                )

                if res_ping.status_code not in (200,):
                    return False #[TODO]

                res_get_node = requests.get(
                    urllib.parse.urljoin(url % addr, '/get_node')
                )

                if res_get_node.status_code not in (200,):
                    return False #[TODO]

                s = json.loads(res_get_node.text)

                self.node.validators.append(Node(s['node_id'], s['address'], s['threshold'], s['validator_addrs']))
                log.info('Init Data Receive! %s, %s' % (s['node_id'], s['endpoint']))

            time.sleep(1)

        return True


class BOSNetHTTPServer(HTTPServer):
    def __init__(self, nd, *a, **kw):
        assert isinstance(nd, Node)

        super(BOSNetHTTPServer, self).__init__(*a, **kw)

        self.nd = nd

        t = Ping(self.nd)
        t.start()

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
