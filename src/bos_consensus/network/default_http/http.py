from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from queue import Queue
import requests
from socketserver import ThreadingMixIn
import threading
import time
import urllib
from urllib.parse import urlparse

from . import handler
from ..base import (
    BaseTransport,
    BaseServer,
)
from ...node import Node
from ...util import logger


class Ping(threading.Thread):
    node = None
    event = None

    def __init__(self, node):
        super(Ping, self).__init__()

        self.node = node
        self.event = threading.Event()
        self.event.set()

        self.log = logger.get_logger('ping', node=self.node.node_id)

    def run(self):
        while self.event.is_set():
            time.sleep(1)

            if self.node.all_validators_connected():
                self.node.init_node()
                break

            for addr, connected in self.node.validators.items():
                if connected:
                    continue

                try:
                    ping_response = requests.get(urllib.parse.urljoin(addr, '/ping'))
                    ping_response.raise_for_status()

                    # validation check
                    get_node_response = requests.get(urllib.parse.urljoin(addr, '/get_node'))
                    get_node_response.raise_for_status()
                    self.node.validators[addr] = True
                    self.log.info("Validator information received from '%s'" % addr)

                except requests.exceptions.ConnectionError:
                    self.log.warn("ConnectionError occurred during validator connection to '%s'!" % addr)
                except requests.exceptions.HTTPError:
                    self.log.warn("HTTPError occurred during validator connection to '%s'!" % addr)
                    continue

        return True


class LockedQueue(Queue):
    def __init__(self, maxsize=0):
        super(LockedQueue, self).__init__(maxsize)
        self.lock = threading.Lock()

    def push_queue(self, element):
        self.lock.acquire()
        self.put(element)
        self.lock.release()
        return

    def pop_queue(self):
        self.lock.acquire()
        element = self.get()
        self.lock.release()
        return element


class Executor(threading.Thread):
    def __init__(self, node, action_queue):
        assert isinstance(node, Node)
        assert isinstance(action_queue, LockedQueue)

        super(Executor, self).__init__()

        self.node = node
        self.action_queue = action_queue

        self.log = logger.get_logger('executor', node=self.node.node_id)

    def run(self):
        while True:
            if self.action_queue.empty():
                time.sleep(1)
            else:
                element = self.action_queue.pop_queue()
                assert isinstance(element, tuple)
                func_name = element[0]
                arg = element[1]

                if not hasattr(self.node, func_name):
                    self.log.error('%s method is not exist in Node object' % func_name)
                func = getattr(self.node, func_name)
                func(arg)
        return True


class NodeManager:
    def __init__(self, node):
        assert isinstance(node, Node)

        self.node = node
        self.action_queue = LockedQueue()
        t = Executor(self.node, self.action_queue)
        t.start()

    def push_element(self, func_name, arg):
        self.action_queue.push_queue((func_name, arg))


class BOSNetHTTPServer(ThreadingMixIn, HTTPServer):
    ping = None

    def __init__(self, node, *a, **kw):
        assert isinstance(node, Node)

        super(BOSNetHTTPServer, self).__init__(*a, **kw)

        self.version = '0.8.1'
        self.lqueue = LockedQueue()
        self.node = node
        self.node_manager = NodeManager(self.node)
        self.ping = self.start_ping()

    def start_ping(self):
        ping = Ping(self.node)
        ping.start()

        return ping

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self.node, request, client_address, self)

        return

    @property
    def endpoint(self):
        return self.node.endpoint

    def node_sequence_executor(self, func_name, arg):
        self.node_manager.push_element(func_name, arg)


class BOSNetHTTPServerRequestHandler(BaseHTTPRequestHandler):
    node = None
    log = None

    def __init__(self, node, *a, **kw):
        self.node = node
        self.log = logger.get_logger('network', node=self.node.node_id)

        super(BOSNetHTTPServerRequestHandler, self).__init__(*a, **kw)

    def do_GET(self):
        self.log.debug('> start request: %s', self.path)
        parsed = urlparse(self.path)
        func = None
        query = parsed.path[1:]
        if len(query) == 0:
            query = 'status'
        func = handler.HTTP_HANDLERS.get(query.split('/')[0], handler.not_found_handler)
        r = func(self, parsed)
        self.log.debug('< pushed request in queue: %s', self.path)
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

    def log_message(self, *a, **kw):
        if self.log.getLevel() == logging.DEBUG:
            super(BOSNetHTTPServerRequestHandler, self).log_message(*a, **kw)

        return


class Transport(BaseTransport):
    http_server_class = BOSNetHTTPServer
    http_request_handler_class = BOSNetHTTPServerRequestHandler

    server = None

    def __init__(self, **config):
        super(Transport, self).__init__(**config)

        assert 'bind' in config
        assert hasattr(config['bind'], '__getitem__')
        assert type(config['bind'][1]) in (int,)

        self.server = None

    def _start(self):
        self.server = self.http_server_class(
            self.node,
            self.config['bind'],
            self.http_request_handler_class,
        )

        self.server.serve_forever()

        return

    def stop(self):
        if self.server.ping is not None:
            self.server.ping.event.clear()

        self.server.server_close()

        return

    def send(self, addr, message):
        self.log.debug('[%s] begin send_to %s' % (self.node.node_id, addr))
        post_data = json.dumps(message)
        try:
            response = requests.post(urllib.parse.urljoin(addr, '/send_ballot'), data=post_data)
            if response.status_code == 200:
                self.log.debug('[%s] sent to %s' % (self.node.node_id, addr))
        except requests.exceptions.ConnectionError:
            self.log.error('[%s] Connection to %s Refused' % (self.node.node_id, addr))

        return


class Server(BaseServer):
    pass
