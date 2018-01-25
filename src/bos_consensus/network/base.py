from ..util import (
    get_module,
    LoggingMixin,
)


def get_network_module(name):
    return get_module('.' + name, package='bos_consensus.network')


class BaseTransport(LoggingMixin):
    blockchain = None
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

    def start(self, blockchain, message_received_callback):
        from ..blockchain.base import BaseBlockchain
        assert isinstance(blockchain, BaseBlockchain)

        self.set_logging('network', node=blockchain.node_name)

        self.blockchain = blockchain
        self.message_received_callback = message_received_callback

        self._start()

        return

    def _start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class BaseServer(LoggingMixin):
    blockchain = None
    transport = None

    config = None

    def __init__(self, blockchain, **config):
        super(BaseServer, self).__init__()

        self.set_logging('network', node=blockchain.node_name)

        self.blockchain = blockchain
        self.config = config

    def start(self):
        self.blockchain.consensus.transport.start(self.blockchain, self.message_received_callback)

        return

    def message_received_callback(self):
        raise NotImplementedError()

    def stop(self):
        self.blockchain.consensus.transport.stop()

        return
