from ..common import Node
from ..util import LoggingMixin
from bos_consensus.network import BaseTransport


class BaseBlockchain(LoggingMixin):
    node = None
    transport = None

    def __init__(self, node, transport):
        assert isinstance(node, Node)
        assert isinstance(transport, BaseTransport)

        super(BaseBlockchain, self).__init__()

        self.node = node
        self.transport = transport

        self.set_logging('blockchain', node=self.node.name)

    def __repr__(self):
        return '<Consensus: %s(%s)>' % (self.node_name, self.endpoint)

    @property
    def node_name(self):
        return self.node.name

    @property
    def endpoint(self):
        return self.node.endpoint

    def to_dict(self):
        return dict(
            node=self.node.to_dict()
        )
