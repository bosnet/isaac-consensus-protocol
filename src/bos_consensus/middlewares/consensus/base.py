import os.path
import pathlib

from bos_consensus.util import (
    get_module,
    LoggingMixin,
)


class NoFurtherConsensusMiddlewares(Exception):
    pass


class StopStore(Exception):
    pass

class StopBroadcast(Exception):
    pass


class BaseConsensusMiddleware(LoggingMixin):
    consensus = None

    def __init__(self, consensus):
        self.consensus = consensus

        super(BaseConsensusMiddleware, self).__init__()
        self.set_logging('consensus_middleware', node=self.consensus.node_name)

    def store(self, ballot):
        pass

    def broadcast(self, ballot):
        pass
