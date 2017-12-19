import requests
import pytest
from bos_consensus.ballot import Ballot
from bos_consensus.network import (
    BOSNetHTTPServer,
    BOSNetHTTPServerRequestHandler,
)
from contextlib import closing
import json
from bos_consensus.node import Node
import socket
from bos_consensus.statekind import StateKind
import threading
import urllib



def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


PORT = find_free_port()
NODE_ID = 52


class Server(threading.Thread):
    httpd = None

    def __init__(self, port, node_id):
        super(Server, self).__init__()
        self.port = port
        self.node_id = node_id

        self.httpd = None

    def run(self):
        node = Node(self.node_id, ('localhost', self.port), 100, ['localhost:5002', 'localhost:5003'])
        self.httpd = BOSNetHTTPServer(node, ('localhost', self.port), BOSNetHTTPServerRequestHandler)
        self.httpd.serve_forever()

        return True


class Client(threading.Thread):
    def __init__(self, port):
        super(Client, self).__init__()
        self.port = port
        self.response_code = 0
        self.url_format = 'http://localhost:%d'

    def run(self):
        self.run_impl()
        return

    def run_impl(self):
        raise NotImplementedError()

    def get_response_code(self):
        return self.response_code


class Ping(Client):
    def __init__(self, port):
        super(Ping, self).__init__(port)

    def run_impl(self):
        try:
            response = requests.get(
                urllib.parse.urljoin(self.url_format % self.port, '/ping')
                )

            self.response_code = response.status_code
        except requests.exceptions.ConnectionError:
            print('Connection Refused!')
        return True


@pytest.fixture(scope='function')
def setup_server(request):
    server_thread = Server(PORT, NODE_ID)
    server_thread.daemon = True
    server_thread.start()

    def teardown():
        server_thread.httpd.server_close()

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
        try:
            response = requests.get(
                urllib.parse.urljoin(self.url_format % self.port, '/status')
                )
            self.response_code = response.status_code
            self.node_id = json.loads(response.text)['Node']['node_id']
        except requests.exceptions.ConnectionError:
            print('Connection Refused!')
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
        try:
            url = 'http://localhost:%d' % self.port
            response = requests.get(
                urllib.parse.urljoin(url, '/get_node')
                )
            self.response_code = response.status_code
            self.node_id = json.loads(response.text)['node_id']
        except requests.exceptions.ConnectionError:
            print('Connection Refused!')
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
        try:
            url = 'http://localhost:%d' % self.port
            post_data = json.dumps({'message': self.message})
            response = requests.post(
                urllib.parse.urljoin(url, '/send_message'),
                data = post_data
                )

            self.response_code = response.status_code
        except requests.exceptions.ConnectionError:
            print('Connection Refused!')
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
        try:
            url = 'http://localhost:%d' % self.port

            post_data = json.dumps(self.ballot.to_dict())
            response = requests.post(
                urllib.parse.urljoin(url, '/send_ballot'),
                data = post_data
                )

            self.response_code = response.status_code
        except requests.exceptions.ConnectionError:
            print('Connection Refused!')
        return True


def test_handler_send_ballot(setup_server):
    ballot = Ballot(1, NODE_ID, 'message', StateKind.INIT)
    client_ping_thread = SendBallot(PORT, ballot)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()

    assert client_ping_thread.get_response_code() == 200
