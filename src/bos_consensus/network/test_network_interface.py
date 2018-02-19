import json
import pytest
import requests
import threading
import time
import traceback
import urllib

from ..common import Ballot, Message, node_factory
from ..blockchain import Blockchain
from ..network import Endpoint, get_network_module
from ..consensus.fba.isaac import IsaacConsensus
from ..consensus.fba.isaac import IsaacState
from ..util import get_free_port, logger, LOG_LEVEL_METRIC


PORT = get_free_port()
NODE_NAME = 'n1'


logger.set_level(LOG_LEVEL_METRIC, 'consensus')


class Server(threading.Thread):
    server = None

    def __init__(self, port, node_name):
        super(Server, self).__init__()
        self.port = port
        self.node_name = node_name

        self.server = None

    def run(self):
        network_module = get_network_module('default_http')

        class TestBOSNetHTTPServer(network_module.BOSNetHTTPServer):
            def start_ping(self):
                return

        class TestTransport(network_module.Transport):
            http_server_class = TestBOSNetHTTPServer

            def set_requests(self):
                self.requests = requests

        node = node_factory(self.node_name, Endpoint('http', 'localhost', self.port))

        validators = list()
        validators_endpoint_uris = ['http://localhost:5002', 'http://localhost:5003']
        for uri in validators_endpoint_uris:
            validators.append(node_factory(uri, Endpoint.from_uri(uri)))

        consensus = IsaacConsensus(node, 100, validators)

        transport = TestTransport(bind=('localhost', self.port))
        blockchain = Blockchain(
            consensus,
            transport
        )

        self.server = network_module.Server(blockchain)
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
    server_thread = Server(PORT, NODE_NAME)
    server_thread.daemon = True
    server_thread.start()

    def teardown():
        if server_thread is None:
            return

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
        self.node_name = None

    def run_impl(self):
        response = requests.get(
            urllib.parse.urljoin(self.url_format % self.port, '/status'),
        )
        self.response_code = response.status_code
        self.node_name = json.loads(response.text)['blockchain']['node']['name']

        return True

    def get_node_name(self):
        return self.node_name


def test_handler_status(setup_server):
    client_ping_thread = Status(PORT)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()
    assert client_ping_thread.get_response_code() == 200
    assert client_ping_thread.get_node_name() == NODE_NAME


class GetNode(Client):
    def __init__(self, port):
        super(GetNode, self).__init__(port)
        self.node_name = 0

    def run_impl(self):
        url = 'http://localhost:%d' % self.port
        response = requests.get(
            urllib.parse.urljoin(url, '/get_node'),
        )
        self.response_code = response.status_code
        self.node_name = json.loads(response.text)['name']

        return True

    def get_node_name(self):
        return self.node_name


def test_handler_get_node(setup_server):
    client_ping_thread = GetNode(PORT)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()
    assert client_ping_thread.get_response_code() == 200
    assert client_ping_thread.get_node_name() == NODE_NAME


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

        post_data = self.ballot.serialize(to_string=True)
        response = requests.post(
            urllib.parse.urljoin(url, '/send_ballot'),
            data=post_data,
        )

        self.response_code = response.status_code

        return True


def test_handler_send_ballot(setup_server):
    message = Message.new('message')
    ballot = Ballot.new(NODE_NAME, message, IsaacState.INIT)

    client_ping_thread = SendBallot(PORT, ballot)
    client_ping_thread.daemon = True
    client_ping_thread.start()
    client_ping_thread.join()

    assert client_ping_thread.get_response_code() == 200
