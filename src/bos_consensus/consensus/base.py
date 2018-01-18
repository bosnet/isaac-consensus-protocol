from ..util import LoggingMixin


class BaseConsensus(LoggingMixin):
    node = None

    def set_node(self, node):
        self.node = node

        self.set_logging('consensus', node=self.node.node_id)

        return

    def initialize(self):
        assert self.node is not None

        return
