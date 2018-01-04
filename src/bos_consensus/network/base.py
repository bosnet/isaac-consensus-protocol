import importlib

from ..node import Node


def get_network_module(name):
    try:
        return importlib.import_module('.' + name, package='bos_consensus.network')
    except ModuleNotFoundError:
        return None


class BaseTransport:
    node = None
    config = None

    message_received_callback = None

    def __init__(self, node, **config):
        assert isinstance(node, Node)

        self.node = node
        self.config = config

    def receive(self, data):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    def send(self, data):
        raise NotImplementedError()

    def start(self, message_received_callback):
        self.message_received_callback = message_received_callback

        return


class BaseServer:
    node = None
    transport = None

    config = None

    def __init__(self, node, transport, **config):
        self.node = node
        self.transport = transport

        self.config = config

    def start(self):
        self.transport.start(self.message_received_callback)

        return

    def message_received_callback(self):
        raise NotImplementedError()

    def stop(self):
        self.transport.stop()

        return
