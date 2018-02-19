from bos_consensus.util import LoggingMixin


class NoFurtherBlockchainMiddlewares(Exception):
    pass


class StopReceiveBallot(Exception):
    pass


class BaseBlockchainMiddleware(LoggingMixin):
    blockchain = None

    def __init__(self, blockchain):
        self.blockchain = blockchain

        super(BaseBlockchainMiddleware, self).__init__()
        self.set_logging('middleware', node=self.blockchain.consensus.node.name)

    def received_ballot(self, ballot):
        pass

    def finished_ballot(self, ballot):
        pass
