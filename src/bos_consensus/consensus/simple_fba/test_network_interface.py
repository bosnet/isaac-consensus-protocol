from contextlib import closing
import json
import pytest
import requests
import socket
import threading
import time
import traceback
import urllib

from bos_consensus.ballot import Ballot
from bos_consensus.network import get_network_module
from .. import get_consensus_module
from ...node import Node
from ...message import Message


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


PORT = find_free_port()
NODE_ID = 52


class Server(threading.Thread):
    server = None

    def __init__(self, port, node_id):
        super(Server, self).__init__()
        self.port = port
        self.node_id = node_id

        self.server = None

    def run(self):
        consensus_module = get_consensus_module('simple_fba')
        node = Node(
            self.node_id,
            ('localhost', self.port),
            100,
            ['localhost:5002', 'localhost:5003'],
            consensus_module.Consensus(),
        )

        network_module = get_network_module('default_http')

        class TestBOSNetHTTPServer(network_module.BOSNetHTTPServer):
            def start_ping(self):
                return

        class TestTransport(network_module.Transport):
            http_server_class = TestBOSNetHTTPServer

        self.server = network_module.Server(
            node,
            TestTransport(bind=('localhost', self.port)),
        )
        self.server.start()

        return True


class Client(threading.Thread):
    def __init__(self, port):
        super(Client, self).__init__()
        self.port = port
        self.response_code = 0
        self.url_format = 'http://localhost:%d'

    def run(self):
        max_tries = 10
        tried = 0
        while tried < max_tries:
            try:
                self.run_impl()
            except requests.exceptions.ConnectionError:
                continue
            except Exception:
                traceback.print_exc()
                break
            else:
                break
            finally:
                tried += 1
                time.sleep(0.1)

        return

    def run_impl(self):
        raise NotImplementedError()

    def get_response_code(self):
        return self.response_code


class Ping(Client):
    def __init__(self, port):
        super(Ping, self).__init__(port)

    def run_impl(self):
        response = requests.get(
            urllib.parse.urljoin(self.url_format % self.port, '/ping'),
        )

        self.response_code = response.status_code

        return True


@pytest.fixture(scope='function')
def setup_server(request):
    server_thread = Server(PORT, NODE_ID)
    server_thread.daemon = True
    server_thread.start()

    def teardown():
        server_thread.server.stop()

        return

    request.addfinalizer(teardown)

    return


def test_handler_ping(setup_server):
    client_ping_thread = Ping(PORT)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()
    assert client_ping_thread.get_response_code() == 200


class Status(Client):
    def __init__(self, port):
        super(Status, self).__init__(port)
        self.node_id = 0

    def run_impl(self):
        response = requests.get(
            urllib.parse.urljoin(self.url_format % self.port, '/status'),
        )
        self.response_code = response.status_code
        self.node_id = json.loads(response.text)['Node']['node_id']

        return True

    def get_node_id(self):
        return self.node_id


def test_handler_status(setup_server):
    client_ping_thread = Status(PORT)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()
    assert client_ping_thread.get_response_code() == 200
    assert client_ping_thread.get_node_id() == NODE_ID


class GetNode(Client):
    def __init__(self, port):
        super(GetNode, self).__init__(port)
        self.node_id = 0

    def run_impl(self):
        url = 'http://localhost:%d' % self.port
        response = requests.get(
            urllib.parse.urljoin(url, '/get_node'),
        )
        self.response_code = response.status_code
        self.node_id = json.loads(response.text)['node_id']

        return True

    def get_node_id(self):
        return self.node_id


def test_handler_get_node(setup_server):
    client_ping_thread = GetNode(PORT)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()
    assert client_ping_thread.get_response_code() == 200
    assert client_ping_thread.get_node_id() == NODE_ID


class SendMessage(Client):
    def __init__(self, port, message):
        super(SendMessage, self).__init__(port)
        self.message = message

    def run_impl(self):
        url = 'http://localhost:%d' % self.port

        response = requests.post(
            urllib.parse.urljoin(url, '/send_message'),
            data=Message.new(self.message).serialize(to_string=True),
        )

        self.response_code = response.status_code

        return True


def test_handler_send_message(setup_server):

    client_ping_thread = SendMessage(PORT, 'message')
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()
    assert client_ping_thread.get_response_code() == 200


class SendBallot(Client):
    def __init__(self, port, ballot):
        super(SendBallot, self).__init__(port)
        self.ballot = ballot

    def run_impl(self):
        url = 'http://localhost:%d' % self.port

        post_data = self.ballot.serialize(None, to_string=True)
        response = requests.post(
            urllib.parse.urljoin(url, '/send_ballot'),
            data=post_data,
        )

        self.response_code = response.status_code

        return True


def test_handler_send_ballot(setup_server):
    StateKind = get_consensus_module('simple_fba').StateKind

    message = Message.new('message')
    ballot = Ballot.new(NODE_ID, message, StateKind.INIT)
    client_ping_thread = SendBallot(PORT, ballot)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()

    assert client_ping_thread.get_response_code() == 200
