import json
import logging
from queue import Queue
import requests
from socketserver import ThreadingMixIn
import threading
import time
import urllib

from bos_consensus.blockchain.base import BaseBlockchain
from http.server import BaseHTTPRequestHandler, HTTPServer
from ..base import (
    Endpoint,
    BaseServer,
    BaseTransport,
)
from . import handler
from ...util import logger
from bos_consensus.common.node import Node


SCHEME = 'http'

MAX_INITIAL_TRIES = 3


class Ping(threading.Thread):
    blockchain = None
    event = None
    initialized = None

    def __init__(self, blockchain):
        assert isinstance(blockchain, BaseBlockchain)

        super(Ping, self).__init__()

        self.blockchain = blockchain
        self.initialized = False

        self.event = threading.Event()
        self.event.set()

        self.log = logger.get_logger('ping', node=self.blockchain.node.name)

    def get_node(self, response):
        data = json.loads(response.text)
        return Node(data['name'], Endpoint.from_uri(data['endpoint']))

    def run(self):
        consensus = self.blockchain.consensus

        connected_nodes = list()

        prev = set()
        n = -1
        while self.event.is_set():
            n += 1
            time.sleep(2)

            now = set(consensus.validators.keys())
            if now != prev:
                if consensus.all_validators_connected():
                    self.log.debug('[%d] all nodes were connected: %s -> %s', n, prev, now)
                else:
                    self.log.debug('[%s] the set of connected validators was changed: %s -> %s', n, prev, now)

            if not self.initialized and (n > MAX_INITIAL_TRIES or consensus.all_validators_connected()):
                consensus.init()
                self.initialized = True

                self.log.debug('consensus was initialized')

            for node in consensus.validator_candidates:
                if node in connected_nodes:
                    continue

                try:
                    ping_response = requests.get(urllib.parse.urljoin(node.endpoint.uri, '/ping'))
                    ping_response.raise_for_status()

                    # validation check
                    get_node_response = requests.get(urllib.parse.urljoin(node.endpoint.uri, '/get_node'))
                    get_node_response.raise_for_status()
                except Exception as e:
                    if node.name not in prev:
                        self.log.error("[%d] failed to connect to %s: %s", n, node, e)

                    consensus.remove_from_validators(node)
                else:
                    consensus.add_to_validators(self.get_node(get_node_response))

                    if node.name not in prev:
                        self.log.debug("[%d] successfully connected to %s", n, node)

            prev = now

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
    def __init__(self, blockchain, action_queue):
        assert isinstance(blockchain, BaseBlockchain)
        assert isinstance(action_queue, LockedQueue)

        super(Executor, self).__init__()
        self.blockchain = blockchain
        self.action_queue = action_queue

        self.log = logger.get_logger('executor', node=self.blockchain.node.name)

    def run(self):
        while True:
            if self.action_queue.empty():
                time.sleep(1)
            else:
                element = self.action_queue.pop_queue()
                assert isinstance(element, tuple)
                func_name = element[0]
                arg = element[1]

                if not hasattr(self.blockchain, func_name):
                    self.log.error('%s method is not exist in Consensus object' % func_name)
                func = getattr(self.blockchain, func_name)
                func(arg)
        return True


class BlockchainManager():
    def __init__(self, blockchain):
        assert isinstance(blockchain, BaseBlockchain)

        self.blockchain = blockchain
        self.action_queue = LockedQueue()
        t = Executor(self.blockchain, self.action_queue)
        t.start()

    def push_element(self, func_name, arg):
        self.action_queue.push_queue((func_name, arg))


class BOSNetHTTPServer(ThreadingMixIn, HTTPServer):
    ping = None

    def __init__(self, blockchain, *a, **kw):
        assert isinstance(blockchain, BaseBlockchain)

        super(BOSNetHTTPServer, self).__init__(*a, **kw)

        self.version = '0.8.1'
        self.lqueue = LockedQueue()
        self.blockchain = blockchain
        self.node_name = blockchain.node_name
        self.blockchain_manager = BlockchainManager(self.blockchain)

        self.start_ping()

    def start_ping(self):
        self.ping = Ping(self.blockchain)
        self.ping.start()

        return

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self.node_name, request, client_address, self)

        return

    @property
    def endpoint(self):
        return self.blockchain.endpoint

    def blockchain_sequence_executor(self, func_name, arg):
        self.blockchain_manager.push_element(func_name, arg)


class BOSNetHTTPServerRequestHandler(BaseHTTPRequestHandler):
    node = None
    log = None

    def __init__(self, node_name, *a, **kw):
        self.node_name = node_name
        self.log = logger.get_logger('http', node=self.node_name)

        super(BOSNetHTTPServerRequestHandler, self).__init__(*a, **kw)

    def _parse_request(self):
        parsed = urllib.parse.urlparse(self.path)
        query = parsed.path[1:]
        if len(query) == 0:
            query = 'status'

        return (query, parsed)

    def do_GET(self):
        self.log.debug('start request: %s', self.path)

        query, parsed = self._parse_request()
        if query is None:
            self.log.debug('pushed request in queue: %s', self.path)
            return self.response(404, 'unknown request')

        func = handler.HTTP_HANDLERS.get(query.split('/')[0], handler.not_found_handler)
        r = func(self, parsed)

        self.log.debug('pushed request in queue: %s', self.path)
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
            self.blockchain,
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

    def send(self, endpoint, data):
        node_name = self.blockchain.node_name
        self.log.debug('[%s] begin send_to %s' % (node_name, endpoint))
        post_data = json.dumps(data)
        try:
            response = requests.post(urllib.parse.urljoin(endpoint.uri, '/send_ballot'), data=post_data)
            if response.status_code == 200:
                self.log.debug('[%s] sent to %s' % (node_name, endpoint))
        except requests.exceptions.ConnectionError:
            self.log.error('[%s] Connection to %s Refused' % (node_name, endpoint))

        return


class Server(BaseServer):
    pass
