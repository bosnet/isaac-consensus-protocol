import urllib.parse

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

        self.set_logging('transport', node=blockchain.node_name)

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


class Endpoint:
    scheme = None
    host = None
    port = None
    extras = None

    @classmethod
    def from_uri(cls, uri):
        parsed = urllib.parse.urlparse(uri)

        return cls(parsed.scheme, parsed.hostname, parsed.port, **urllib.parse.parse_qs(parsed.query))

    def __init__(self, scheme, host, port, **extras):
        assert type(host) in (str,)
        assert type(port) in (int,)

        self.scheme = scheme
        self.host = host
        self.port = port
        self.extras = extras

    @property
    def uri_full(self):
        extras = None
        if self.extras:
            extras = '?%s' % urllib.parse.urlencode(self.extras)

        return '%s%s' % (self.uri, extras)

    @property
    def uri(self):
        return '%(scheme)s://%(host)s:%(port)d' % self.__dict__

    def __repr__(self):
        return '<Endpoint: %s>' % self.uri_full

    def __eq__(self, b):
        assert isinstance(b, self.__class__)

        return self.host == b.host and self.port == b.port

    def update(self, **extras):
        self.extras.update(extras)

        return

    def serialize(self):
        return self.uri_full

    def get(self, k, default=None):
        return self.extras.get(k, default)
