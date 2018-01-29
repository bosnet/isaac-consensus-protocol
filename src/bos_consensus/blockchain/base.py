from ..network import BaseTransport
from ..common.node import Node
from ..util import LoggingMixin


class BaseBlockchain(LoggingMixin):
    node = None

    def __init__(self, node):
        assert isinstance(node, Node)

        super(BaseBlockchain, self).__init__()

        self.node = node

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
