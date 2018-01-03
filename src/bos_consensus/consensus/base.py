class BaseConsensus:
    node = None

    def set_node(self, node):
        self.node = node

        return

    def initialize(self):
        assert self.node is not None

        return
