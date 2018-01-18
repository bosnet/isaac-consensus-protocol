import importlib

from ..util import LoggingMixin


def get_network_module(name):
    try:
        return importlib.import_module('.' + name, package='bos_consensus.network')
    except ModuleNotFoundError:
        return None


class BaseTransport(LoggingMixin):
    node = None
    config = None

    message_received_callback = None

    def __init__(self, **config):
        super(BaseTransport, self).__init__()

        self.config = config

    def receive(self, data):
        raise NotImplementedError()

    def write(self, data):
        raise NotImplementedError()

    def send(self, addr, message):
        raise NotImplementedError()

    def start(self, node, message_received_callback):
        from ..node import Node
        assert isinstance(node, Node)

        self.set_logging('network', node=node.node_id)

        self.node = node
        self.message_received_callback = message_received_callback

        self._start()

        return

    def _start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class BaseServer(LoggingMixin):
    node = None
    transport = None

    config = None

    def __init__(self, node, transport, **config):
        super(BaseServer, self).__init__()

        self.set_logging('network', node=node.node_id)

        self.node = node
        self.transport = transport
        self.node.set_transport(transport)

        self.config = config

    def start(self):
        self.transport.start(self.node, self.message_received_callback)

        return

    def message_received_callback(self):
        raise NotImplementedError()

    def stop(self):
        self.transport.stop()

        return
